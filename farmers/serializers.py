from rest_framework import serializers
from .models import Farmer, FarmerSupply
from products.serializers import ProductSerializer
import re


class FarmerSerializer(serializers.ModelSerializer):
    """Serializer for Farmer model"""
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = Farmer
        fields = ['id', 'profile_picture', 'full_name', 'mobile_number', 'ghana_card_number',
                  'gps_latitude', 'gps_longitude', 'region', 'district', 'community',
                  'maize_types_supplied', 'notes', 'is_approved', 'is_active',
                  'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def validate_ghana_card_number(self, value):
        pattern = r'^GHA-\d{9}-\d$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Invalid Ghana Card format. Use: GHA-123456789-0")
        return value
    
    def validate_gps_latitude(self, value):
        if not (-90 <= float(value) <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value
    
    def validate_gps_longitude(self, value):
        if not (-180 <= float(value) <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value


class FarmerSupplySerializer(serializers.ModelSerializer):
    """Serializer for FarmerSupply model"""
    farmer_name = serializers.CharField(source='farmer.full_name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    balance_due = serializers.ReadOnlyField()
    
    class Meta:
        model = FarmerSupply
        fields = ['id', 'farmer', 'farmer_name', 'product', 'product_name',
                  'quantity_bags', 'quantity_tons', 'date_delivered', 'cost_per_bag',
                  'total_cost', 'payment_status', 'amount_paid', 'balance_due',
                  'stock', 'notes', 'recorded_by', 'recorded_by_name',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'total_cost', 'recorded_by', 'stock', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        if attrs.get('amount_paid', 0) > attrs.get('total_cost', 0):
            raise serializers.ValidationError({"amount_paid": "Amount paid cannot exceed total cost"})
        return attrs


class RecordPaymentSerializer(serializers.Serializer):
    """Serializer for recording farmer payment"""
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greater than 0")
        return value
