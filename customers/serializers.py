from rest_framework import serializers
from .models import Customer
from accounts.serializers import UserSerializer


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model"""
    user = UserSerializer(read_only=True)
    total_orders = serializers.ReadOnlyField()
    total_spent = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = ['id', 'user', 'customer_id', 'location', 'is_active',
                  'total_orders', 'total_spent', 'created_at', 'updated_at']
        read_only_fields = ['id', 'customer_id', 'created_at', 'updated_at']


class CustomerUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating customer profile"""
    
    class Meta:
        model = Customer
        fields = ['location']
