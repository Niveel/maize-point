from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    current_stock = serializers.ReadOnlyField()
    current_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'packaging_sizes', 'is_available',
                  'current_stock', 'current_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_current_price(self, obj):
        price = obj.current_price
        if price:
            return {
                'price_per_bag': str(price.price_per_bag),
                'price_per_ton': str(price.price_per_ton),
                'packaging_size': price.packaging_size,
            }
        return None
    
    def validate_packaging_sizes(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Packaging sizes must be a list.")
        if not value:
            raise serializers.ValidationError("At least one packaging size is required.")
        return value
