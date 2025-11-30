from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from datetime import timedelta
from .models import Stock, StockMovement
from .serializers import StockSerializer, StockMovementSerializer


class IsAdminOrStaff(permissions.BasePermission):
    """Only admin and staff can access"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in ['ADMIN', 'STAFF']


class StockViewSet(viewsets.ModelViewSet):
    """ViewSet for Stock model"""
    queryset = Stock.objects.select_related('product', 'farmer').all()
    serializer_class = StockSerializer
    permission_classes = [IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product', 'warehouse_location', 'source_type']
    search_fields = ['product__name', 'warehouse_location']
    ordering_fields = ['date_received', 'quantity_bags']
    ordering = ['-date_received']
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """Get low stock and expiry alerts"""
        # Low stock items
        low_stock = self.queryset.filter(quantity_bags__lt=100)
        
        # Expiring soon (within 30 days)
        expiry_date = timezone.now().date() + timedelta(days=30)
        expiring_soon = self.queryset.filter(
            expiry_alert_date__lte=expiry_date,
            expiry_alert_date__gte=timezone.now().date()
        )
        
        return Response({
            'low_stock': StockSerializer(low_stock, many=True).data,
            'expiring_soon': StockSerializer(expiring_soon, many=True).data,
        })
    
    @action(detail=False, methods=['post'])
    def deduct(self, request):
        """Manual stock deduction"""
        stock_id = request.data.get('stock_id')
        quantity_bags = request.data.get('quantity_bags')
        quantity_tons = request.data.get('quantity_tons')
        reason = request.data.get('reason', '')
        
        try:
            stock = Stock.objects.get(id=stock_id)
        except Stock.DoesNotExist:
            return Response({'error': 'Stock not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if stock.quantity_bags < quantity_bags:
            return Response(
                {'error': 'Insufficient stock.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Deduct stock
        stock.quantity_bags -= quantity_bags
        stock.quantity_tons -= quantity_tons
        stock.save()
        
        # Create movement record
        StockMovement.objects.create(
            stock=stock,
            movement_type='DEDUCTION',
            quantity_bags=quantity_bags,
            quantity_tons=quantity_tons,
            reason=reason,
            performed_by=request.user
        )
        
        return Response({
            'message': 'Stock deducted successfully.',
            'stock': StockSerializer(stock).data
        })
    
    @action(detail=False, methods=['post'])
    def transfer(self, request):
        """Transfer stock between warehouses"""
        stock_id = request.data.get('stock_id')
        new_location = request.data.get('new_location')
        reason = request.data.get('reason', 'Warehouse transfer')
        
        try:
            stock = Stock.objects.get(id=stock_id)
        except Stock.DoesNotExist:
            return Response({'error': 'Stock not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        old_location = stock.warehouse_location
        stock.warehouse_location = new_location
        stock.save()
        
        # Create movement record
        StockMovement.objects.create(
            stock=stock,
            movement_type='TRANSFER',
            quantity_bags=0,
            quantity_tons=0,
            reason=f"Transfer from {old_location} to {new_location}: {reason}",
            performed_by=request.user
        )
        
        return Response({
            'message': 'Stock transferred successfully.',
            'stock': StockSerializer(stock).data
        })


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for StockMovement model (read-only)"""
    queryset = StockMovement.objects.select_related('stock__product', 'performed_by').all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['stock', 'movement_type']
    ordering = ['-created_at']
