from rest_framework import serializers
from .models import Order
from customers.serializers import CustomerSerializer
from products.serializers import ProductSerializer


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model"""
    customer_details = CustomerSerializer(source='customer', read_only=True)
    product_details = ProductSerializer(source='product', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_id', 'customer', 'customer_details', 'product', 'product_details',
                  'quantity_bags', 'quantity_tons', 'unit_price', 'total_price',
                  'delivery_method', 'delivery_address', 'delivery_date', 'payment_option',
                  'order_status', 'customer_notes', 'admin_notes', 'approved_by',
                  'approved_by_name', 'approved_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'order_id', 'total_price', 'approved_by', 'approved_at',
                           'created_at', 'updated_at']
    
    def validate(self, attrs):
        if attrs.get('delivery_method') == 'DELIVERY' and not attrs.get('delivery_address'):
            raise serializers.ValidationError({
                "delivery_address": "Delivery address is required for delivery orders."
            })
        return attrs


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders (customers)"""
    
    class Meta:
        model = Order
        fields = ['product', 'quantity_bags', 'quantity_tons', 'unit_price',
                  'delivery_method', 'delivery_address', 'payment_option', 'customer_notes']
    
    def validate(self, attrs):
        # Check if product is available
        product = attrs.get('product')
        if not product.is_available:
            raise serializers.ValidationError({"product": "This product is currently not available."})
        
        # Check if price matches current price
        current_price = product.current_price
        if not current_price:
            raise serializers.ValidationError({"product": "No price set for this product."})
        
        return attrs


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating order status"""
    status = serializers.ChoiceField(choices=Order.ORDER_STATUS_CHOICES)
    admin_notes = serializers.CharField(required=False, allow_blank=True)
