from rest_framework import serializers
from .models import Price
from products.serializers import ProductSerializer


class PriceSerializer(serializers.ModelSerializer):
    """Serializer for Price model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.full_name', read_only=True)
    
    class Meta:
        model = Price
        fields = ['id', 'product', 'product_name', 'price_per_bag', 'price_per_ton',
                  'packaging_size', 'market_notes', 'effective_date', 'updated_by',
                  'updated_by_name', 'is_current']
        read_only_fields = ['id', 'effective_date', 'updated_by']
    
    def validate(self, attrs):
        if attrs.get('price_per_bag') and attrs['price_per_bag'] <= 0:
            raise serializers.ValidationError({"price_per_bag": "Price must be greater than 0"})
        if attrs.get('price_per_ton') and attrs['price_per_ton'] <= 0:
            raise serializers.ValidationError({"price_per_ton": "Price must be greater than 0"})
        return attrs


class CurrentPriceSerializer(serializers.ModelSerializer):
    """Serializer for current prices"""
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = Price
        fields = ['id', 'product', 'price_per_bag', 'price_per_ton', 'packaging_size',
                  'market_notes', 'effective_date']
