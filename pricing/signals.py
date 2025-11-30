from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Price
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Price)
def update_price_current_flag(sender, instance, created, **kwargs):
    """Update is_current flag for other prices when a new price is set as current"""
    if instance.is_current and not kwargs.get('raw', False):
        # This is handled in the model's save method, but we log it here
        logger.info(f"New current price set for {instance.product.name} - {instance.packaging_size}")
