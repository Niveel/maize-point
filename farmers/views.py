from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Q
from .models import Farmer, FarmerSupply
from .serializers import FarmerSerializer, FarmerSupplySerializer, RecordPaymentSerializer
from inventory.models import Stock


class IsAdminOrStaff(permissions.BasePermission):
    """Only admin and staff can access"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in ['ADMIN', 'STAFF']


class FarmerViewSet(viewsets.ModelViewSet):
    """ViewSet for Farmer model"""
    queryset = Farmer.objects.select_related('created_by').all()
    serializer_class = FarmerSerializer
    permission_classes = [IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['region', 'district', 'is_approved', 'is_active']
    search_fields = ['full_name', 'mobile_number', 'community', 'ghana_card_number']
    ordering_fields = ['full_name', 'created_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        # Soft delete by setting is_active to False
        instance.is_active = False
        instance.save()
    
    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        """Approve a farmer"""
        farmer = self.get_object()
        farmer.is_approved = True
        farmer.save()
        return Response({'message': 'Farmer approved successfully.'})
    
    @action(detail=True, methods=['get'])
    def supply_history(self, request, pk=None):
        """Get farmer supply history"""
        farmer = self.get_object()
        supplies = FarmerSupply.objects.filter(farmer=farmer).select_related('product', 'recorded_by')
        serializer = FarmerSupplySerializer(supplies, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def record_supply(self, request, pk=None):
        """Record farmer supply and automatically create stock"""
        farmer = self.get_object()
        
        if not farmer.is_approved:
            return Response(
                {'error': 'Farmer must be approved before recording supply.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = FarmerSupplySerializer(data=request.data)
        if serializer.is_valid():
            # Create stock entry first
            stock = Stock.objects.create(
                product=serializer.validated_data['product'],
                quantity_bags=serializer.validated_data['quantity_bags'],
                quantity_tons=serializer.validated_data['quantity_tons'],
                source_type='FARMER',
                farmer=farmer,
                quality_grade=request.data.get('quality_grade', 'Standard'),
                moisture_content=request.data.get('moisture_content', 14.0),
                warehouse_location=request.data.get('warehouse_location', 'Main Warehouse'),
                cost_price=serializer.validated_data['cost_per_bag'],
                date_received=serializer.validated_data['date_delivered'],
                notes=serializer.validated_data.get('notes', '')
            )
            
            # Create farmer supply record
            supply = serializer.save(
                farmer=farmer,
                recorded_by=request.user,
                stock=stock
            )
            
            return Response(
                FarmerSupplySerializer(supply).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def record_payment(self, request, pk=None):
        """Record payment to farmer for a specific supply"""
        farmer = self.get_object()
        supply_id = request.data.get('supply_id')
        
        if not supply_id:
            return Response(
                {'error': 'supply_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            supply = FarmerSupply.objects.get(id=supply_id, farmer=farmer)
        except FarmerSupply.DoesNotExist:
            return Response(
                {'error': 'Supply not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = RecordPaymentSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            
            if supply.amount_paid + amount > supply.total_cost:
                return Response(
                    {'error': 'Payment amount exceeds balance due.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            supply.amount_paid += amount
            if supply.amount_paid >= supply.total_cost:
                supply.payment_status = 'PAID'
            elif supply.amount_paid > 0:
                supply.payment_status = 'PARTIAL'
            supply.save()
            
            return Response({
                'message': 'Payment recorded successfully.',
                'supply': FarmerSupplySerializer(supply).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def reports(self, request):
        """Generate farmer reports"""
        farmers = self.get_queryset()
        
        total_farmers = farmers.count()
        approved_farmers = farmers.filter(is_approved=True).count()
        active_farmers = farmers.filter(is_active=True).count()
        
        # Supplies summary
        supplies_summary = FarmerSupply.objects.aggregate(
            total_supplies=Sum('quantity_bags'),
            total_cost=Sum('total_cost'),
            total_paid=Sum('amount_paid')
        )
        
        return Response({
            'total_farmers': total_farmers,
            'approved_farmers': approved_farmers,
            'active_farmers': active_farmers,
            'supplies_summary': supplies_summary,
        })
