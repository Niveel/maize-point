from rest_framework import serializers
from .models import Stock, StockMovement


class StockSerializer(serializers.ModelSerializer):
    """Serializer for Stock model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    farmer_name = serializers.CharField(source='farmer.full_name', read_only=True, allow_null=True)
    is_low_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Stock
        fields = ['id', 'product', 'product_name', 'quantity_bags', 'quantity_tons',
                  'source_type', 'farmer', 'farmer_name', 'quality_grade', 'moisture_content',
                  'warehouse_location', 'cost_price', 'date_received', 'expiry_alert_date',
                  'notes', 'is_low_stock', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for StockMovement model"""
    stock_product_name = serializers.CharField(source='stock.product.name', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.full_name', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = ['id', 'stock', 'stock_product_name', 'movement_type', 'quantity_bags',
                  'quantity_tons', 'order', 'reason', 'performed_by', 'performed_by_name',
                  'created_at']
        read_only_fields = ['id', 'performed_by', 'created_at']
