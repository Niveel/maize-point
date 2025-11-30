from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FarmerSupply
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=FarmerSupply)
def log_farmer_supply(sender, instance, created, **kwargs):
    """Log farmer supply creation"""
    if created:
        logger.info(
            f"New supply recorded: {instance.farmer.full_name} - "
            f"{instance.product.name} - {instance.quantity_bags} bags"
        )
