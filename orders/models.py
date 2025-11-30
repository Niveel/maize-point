from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from customers.models import Customer
from products.models import Product
import uuid


class Order(models.Model):
    """Order model for customer orders"""
    
    DELIVERY_METHOD_CHOICES = (
        ('PICKUP', 'Pickup'),
        ('DELIVERY', 'Delivery'),
    )
    
    PAYMENT_OPTION_CHOICES = (
        ('CASH', 'Cash'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('MOBILE_MONEY', 'Mobile Money'),
    )
    
    ORDER_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('DISPATCHED', 'Dispatched'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    
    order_id = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders')
    quantity_bags = models.IntegerField(validators=[MinValueValidator(1)])
    quantity_tons = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0.001)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHOD_CHOICES)
    delivery_address = models.TextField(blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    payment_option = models.CharField(max_length=20, choices=PAYMENT_OPTION_CHOICES)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_orders'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_id']),
            models.Index(fields=['customer', 'order_status']),
            models.Index(fields=['order_status']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate unique order ID
            self.order_id = f"ORD{uuid.uuid4().hex[:10].upper()}"
        
        # Auto-calculate total_price
        if self.unit_price and self.quantity_bags:
            self.total_price = self.unit_price * self.quantity_bags
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.order_id} - {self.customer.user.full_name} - {self.product.name}"
