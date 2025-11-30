from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from products.models import Product


class Stock(models.Model):
    """Stock model for inventory management"""
    
    SOURCE_TYPE_CHOICES = (
        ('FARMER', 'Farmer Supply'),
        ('MARKET_PURCHASE', 'Market Purchase'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_items')
    quantity_bags = models.IntegerField(validators=[MinValueValidator(0)])
    quantity_tons = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0)])
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    farmer = models.ForeignKey('farmers.Farmer', on_delete=models.SET_NULL, null=True, blank=True, related_name='stocks')
    quality_grade = models.CharField(max_length=50, default='Standard')
    moisture_content = models.DecimalField(max_digits=5, decimal_places=2, help_text='Moisture percentage')
    warehouse_location = models.CharField(max_length=200)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_received = models.DateTimeField()
    expiry_alert_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stock'
        ordering = ['-date_received']
        indexes = [
            models.Index(fields=['product', 'warehouse_location']),
            models.Index(fields=['date_received']),
            models.Index(fields=['expiry_alert_date']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity_bags} bags - {self.warehouse_location}"
    
    @property
    def is_low_stock(self):
        return self.quantity_bags < 100  # Alert if less than 100 bags


class StockMovement(models.Model):
    """Model for tracking stock movements"""
    
    MOVEMENT_TYPE_CHOICES = (
        ('ADDITION', 'Addition'),
        ('DEDUCTION', 'Deduction'),
        ('TRANSFER', 'Transfer'),
        ('DAMAGE', 'Damage/Loss'),
    )
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantity_bags = models.IntegerField()
    quantity_tons = models.DecimalField(max_digits=10, decimal_places=3)
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movements')
    reason = models.TextField()
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_movements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stock', 'movement_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.stock.product.name} - {self.quantity_bags} bags"
