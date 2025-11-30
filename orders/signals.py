from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, **kwargs):
    """Send email notification when order is created or status changes"""
    try:
        if created:
            # Send order confirmation email to customer
            subject = f'Order Confirmation - {instance.order_id}'
            message = f"""
            Dear {instance.customer.user.full_name},
            
            Your order has been successfully placed!
            
            Order ID: {instance.order_id}
            Product: {instance.product.name}
            Quantity: {instance.quantity_bags} bags
            Total Price: GHS {instance.total_price}
            Status: {instance.get_order_status_display()}
            
            We will process your order shortly.
            
            Thank you for choosing Maize Supply & Storage Enterprise!
            
            Best regards,
            Maize Supply Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.customer.user.email],
                fail_silently=False,
            )
            
            logger.info(f"Order confirmation email sent for {instance.order_id}")
        
        else:
            # Send status update email
            if instance.order_status in ['PROCESSING', 'DISPATCHED', 'DELIVERED', 'CANCELLED']:
                subject = f'Order Status Update - {instance.order_id}'
                message = f"""
                Dear {instance.customer.user.full_name},
                
                Your order status has been updated:
                
                Order ID: {instance.order_id}
                New Status: {instance.get_order_status_display()}
                
                {"Your order is being prepared for delivery." if instance.order_status == 'PROCESSING' else ""}
                {"Your order has been dispatched!" if instance.order_status == 'DISPATCHED' else ""}
                {"Your order has been delivered. Thank you!" if instance.order_status == 'DELIVERED' else ""}
                {"Your order has been cancelled." if instance.order_status == 'CANCELLED' else ""}
                
                Best regards,
                Maize Supply Team
                """
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.customer.user.email],
                    fail_silently=False,
                )
                
                logger.info(f"Order status update email sent for {instance.order_id}")
    
    except Exception as e:
        logger.error(f"Failed to send order notification for {instance.order_id}: {str(e)}")
