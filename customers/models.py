from django.db import models
from django.conf import settings
import uuid


class Customer(models.Model):
    """Customer model linked to User"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_profile'
    )
    customer_id = models.CharField(max_length=20, unique=True, editable=False)
    location = models.CharField(max_length=255, help_text='Customer location/address')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_id']),
            models.Index(fields=['is_active']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.customer_id:
            # Generate unique customer ID
            self.customer_id = f"CUST{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.customer_id} - {self.user.full_name}"
    
    @property
    def total_orders(self):
        return self.orders.count()
    
    @property
    def total_spent(self):
        from orders.models import Order
        return self.orders.filter(
            order_status__in=['DELIVERED']
        ).aggregate(total=models.Sum('total_price'))['total'] or 0
