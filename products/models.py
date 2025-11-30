from django.db import models


class Product(models.Model):
    """Product model for maize types"""
    name = models.CharField(max_length=200, unique=True, help_text='Product name (e.g., Yellow Maize, White Maize)')
    description = models.TextField(help_text='Detailed product description')
    packaging_sizes = models.JSONField(
        default=list,
        help_text='List of available packaging sizes (e.g., ["50kg bag", "100kg bag", "1 ton"])'
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_available']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def current_stock(self):
        """Get current total stock for this product"""
        return self.stock_items.aggregate(
            total_bags=models.Sum('quantity_bags'),
            total_tons=models.Sum('quantity_tons')
        )
    
    @property
    def current_price(self):
        """Get current price for this product"""
        return self.prices.filter(is_current=True).first()
