from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Customer
from .serializers import CustomerSerializer, CustomerUpdateSerializer


class IsAdminOrOwner(permissions.BasePermission):
    """Custom permission: Admin can access all, customers can access only their own"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        if request.user.user_type == 'ADMIN':
            return True
        return obj.user == request.user


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for Customer model"""
    queryset = Customer.objects.select_related('user').all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminOrOwner]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'ADMIN':
            return self.queryset
        # Customers can only see their own profile
        return self.queryset.filter(user=user)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Get or update current customer's profile"""
        try:
            customer = Customer.objects.select_related('user').get(user=request.user)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        else:
            serializer = CustomerUpdateSerializer(
                customer,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(CustomerSerializer(customer).data)
