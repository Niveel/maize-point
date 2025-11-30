from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import User
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def send_registration_email(sender, instance, created, **kwargs):
    """Send welcome email when a new customer registers"""
    if created and instance.user_type == 'CUSTOMER':
        try:
            subject = 'Welcome to Maize Supply & Storage Enterprise'
            message = f"""
            Dear {instance.full_name},
            
            Welcome to Maize Supply & Storage Enterprise!
            
            Your account has been successfully created. You can now place orders and manage your profile.
            
            Username: {instance.username}
            Email: {instance.email}
            
            If you have any questions, please don't hesitate to contact us.
            
            Best regards,
            Maize Supply & Storage Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=False,
            )
            logger.info(f"Registration email sent to {instance.email}")
        except Exception as e:
            logger.error(f"Failed to send registration email to {instance.email}: {str(e)}")
