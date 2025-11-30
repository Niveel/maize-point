from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Customer
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_profile(sender, instance, created, **kwargs):
    """Automatically create Customer profile when a CUSTOMER user is created"""
    if created and instance.user_type == 'CUSTOMER':
        try:
            Customer.objects.create(user=instance)
            logger.info(f"Customer profile created for user {instance.username}")
        except Exception as e:
            logger.error(f"Failed to create customer profile for {instance.username}: {str(e)}")
