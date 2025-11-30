from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Sum, Q
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer
from inventory.models import Stock, StockMovement
import logging

logger = logging.getLogger(__name__)


class IsAdminOrStaffOrOwner(permissions.BasePermission):
    """Admin/staff see all, customers see only their own"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.user_type in ['ADMIN', 'STAFF']:
            return True
        return obj.customer.user == request.user


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Order model"""
    queryset = Order.objects.select_related(
        'customer__user', 'product', 'approved_by'
    ).all()
    permission_classes = [IsAdminOrStaffOrOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['order_status', 'payment_option', 'delivery_method', 'product']
    search_fields = ['order_id', 'customer__user__first_name', 'customer__user__last_name']
    ordering_fields = ['created_at', 'total_price']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type in ['ADMIN', 'STAFF']:
            return self.queryset
        # Customers see only their own orders
        return self.queryset.filter(customer__user=user)
    
    def perform_create(self, serializer):
        # Get customer profile for the current user
        customer = self.request.user.customer_profile
        serializer.save(customer=customer)
    
    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        """Approve order and deduct from stock"""
        order = self.get_object()
        
        if order.order_status != 'PENDING':
            return Response(
                {'error': 'Only pending orders can be approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if sufficient stock is available
        available_stock = Stock.objects.filter(
            product=order.product
        ).aggregate(total=Sum('quantity_bags'))['total'] or 0
        
        if available_stock < order.quantity_bags:
            return Response(
                {'error': f'Insufficient stock. Available: {available_stock} bags, Required: {order.quantity_bags} bags'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Deduct from stock (FIFO - First In, First Out)
        remaining_to_deduct = order.quantity_bags
        remaining_tons = order.quantity_tons
        
        stocks = Stock.objects.filter(
            product=order.product,
            quantity_bags__gt=0
        ).order_by('date_received')
        
        for stock in stocks:
            if remaining_to_deduct <= 0:
                break
            
            deduct_bags = min(stock.quantity_bags, remaining_to_deduct)
            deduct_tons = (deduct_bags / order.quantity_bags) * order.quantity_tons
            
            stock.quantity_bags -= deduct_bags
            stock.quantity_tons -= deduct_tons
            stock.save()
            
            # Create stock movement record
            StockMovement.objects.create(
                stock=stock,
                movement_type='DEDUCTION',
                quantity_bags=deduct_bags,
                quantity_tons=deduct_tons,
                order=order,
                reason=f"Order {order.order_id} approved",
                performed_by=request.user
            )
            
            remaining_to_deduct -= deduct_bags
            remaining_tons -= deduct_tons
        
        # Update order status
        order.order_status = 'PROCESSING'
        order.approved_by = request.user
        order.approved_at = timezone.now()
        order.save()
        
        logger.info(f"Order {order.order_id} approved by {request.user.username}")
        
        return Response({
            'message': 'Order approved and stock deducted successfully.',
            'order': OrderSerializer(order).data
        })
    
    @action(detail=True, methods=['patch'])
    def cancel(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()
        
        if order.order_status in ['DELIVERED', 'CANCELLED']:
            return Response(
                {'error': f'Cannot cancel {order.get_order_status_display().lower()} order.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.order_status = 'CANCELLED'
        order.admin_notes = request.data.get('admin_notes', order.admin_notes)
        order.save()
        
        return Response({
            'message': 'Order cancelled successfully.',
            'order': OrderSerializer(order).data
        })
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update order status (Admin/Staff only)"""
        if request.user.user_type not in ['ADMIN', 'STAFF']:
            return Response(
                {'error': 'Only admin or staff can update order status.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            order.order_status = serializer.validated_data['status']
            order.admin_notes = serializer.validated_data.get('admin_notes', order.admin_notes)
            order.save()
            
            return Response({
                'message': 'Order status updated successfully.',
                'order': OrderSerializer(order).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get order history for current customer"""
        if hasattr(request.user, 'customer_profile'):
            orders = self.queryset.filter(customer=request.user.customer_profile)
            serializer = self.get_serializer(orders, many=True)
            return Response(serializer.data)
        return Response({'error': 'Customer profile not found.'}, status=status.HTTP_404_NOT_FOUND)
