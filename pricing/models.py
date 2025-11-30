from django.db import models
from django.conf import settings
from products.models import Product


class Price(models.Model):
    """Price model for product pricing"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    price_per_bag = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price per bag (GHS)')
    price_per_ton = models.DecimalField(max_digits=12, decimal_places=2, help_text='Price per ton (GHS)')
    packaging_size = models.CharField(max_length=50, help_text='e.g., 50kg bag, 100kg bag')
    market_notes = models.TextField(blank=True, help_text='Market conditions or notes')
    effective_date = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    is_current = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'prices'
        ordering = ['-effective_date']
        indexes = [
            models.Index(fields=['product', 'is_current']),
            models.Index(fields=['effective_date']),
        ]
        unique_together = [['product', 'packaging_size', 'is_current']]
    
    def __str__(self):
        return f"{self.product.name} - {self.packaging_size} - GHS {self.price_per_bag}/bag"
    
    def save(self, *args, **kwargs):
        if self.is_current:
            # Set all other prices for this product and packaging to not current
            Price.objects.filter(
                product=self.product,
                packaging_size=self.packaging_size,
                is_current=True
            ).update(is_current=False)
        super().save(*args, **kwargs)
