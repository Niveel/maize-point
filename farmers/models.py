from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from products.models import Product
import re


class Farmer(models.Model):
    """Farmer model for managing farmer information"""
    profile_picture = models.ImageField(upload_to='farmer_profiles/', null=True, blank=True)
    full_name = models.CharField(max_length=255)
    mobile_number = PhoneNumberField(unique=True, region='GH')
    ghana_card_number = models.CharField(
        max_length=20,
        unique=True,
        help_text='Ghana Card Number (e.g., GHA-123456789-0)'
    )
    gps_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text='GPS Latitude'
    )
    gps_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text='GPS Longitude'
    )
    region = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    community = models.CharField(max_length=100)
    maize_types_supplied = models.JSONField(
        default=list,
        help_text='List of maize types supplied (e.g., ["Yellow Maize", "White Maize"])'
    )
    notes = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='farmers_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'farmers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['mobile_number']),
            models.Index(fields=['ghana_card_number']),
            models.Index(fields=['region', 'district']),
            models.Index(fields=['is_approved', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.community}, {self.district}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Validate Ghana Card format
        if self.ghana_card_number:
            pattern = r'^GHA-\d{9}-\d$'
            if not re.match(pattern, self.ghana_card_number):
                raise ValidationError({
                    'ghana_card_number': 'Invalid Ghana Card format. Use: GHA-123456789-0'
                })


class FarmerSupply(models.Model):
    """Model for recording farmer supply deliveries"""
    
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partial'),
        ('PAID', 'Paid'),
    )
    
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='supplies')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_bags = models.IntegerField(validators=[MinValueValidator(1)])
    quantity_tons = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0.001)])
    date_delivered = models.DateTimeField()
    cost_per_bag = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock = models.ForeignKey('inventory.Stock', on_delete=models.SET_NULL, null=True, blank=True, related_name='farmer_supplies')
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'farmer_supplies'
        ordering = ['-date_delivered']
        indexes = [
            models.Index(fields=['farmer', 'date_delivered']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['product']),
        ]
        verbose_name_plural = 'Farmer Supplies'
    
    def __str__(self):
        return f"{self.farmer.full_name} - {self.product.name} - {self.quantity_bags} bags"
    
    @property
    def balance_due(self):
        return self.total_cost - self.amount_paid
    
    def save(self, *args, **kwargs):
        # Auto-calculate total_cost
        if self.cost_per_bag and self.quantity_bags:
            self.total_cost = self.cost_per_bag * self.quantity_bags
        super().save(*args, **kwargs)
