from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Price
from .serializers import PriceSerializer, CurrentPriceSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read-only for anyone, write for admins only"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.user_type == 'ADMIN'


class PriceViewSet(viewsets.ModelViewSet):
    """ViewSet for Price model"""
    queryset = Price.objects.select_related('product', 'updated_by').all()
    serializer_class = PriceSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['product', 'is_current', 'packaging_size']
    ordering_fields = ['effective_date', 'price_per_bag']
    ordering = ['-effective_date']
    
    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current prices for all products"""
        prices = Price.objects.filter(is_current=True).select_related('product', 'updated_by')
        serializer = CurrentPriceSerializer(prices, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get price history"""
        product_id = request.query_params.get('product')
        queryset = self.queryset
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
