from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StockMovement
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=StockMovement)
def log_stock_movement(sender, instance, created, **kwargs):
    """Log stock movements"""
    if created:
        logger.info(
            f"Stock movement: {instance.get_movement_type_display()} - "
            f"{instance.stock.product.name} - {instance.quantity_bags} bags"
        )
