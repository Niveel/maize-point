from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from inventory.models import Stock


class Command(BaseCommand):
    help = 'Check for low stock and expiring items'

    def handle(self, *args, **kwargs):
        self.stdout.write('Checking stock alerts...\n')
        
        # Low stock check (less than 100 bags)
        low_stock_items = Stock.objects.filter(quantity_bags__lt=100)
        
        if low_stock_items.exists():
            self.stdout.write(self.style.WARNING('LOW STOCK ALERTS:'))
            for item in low_stock_items:
                self.stdout.write(
                    f'  ⚠ {item.product.name} - {item.quantity_bags} bags remaining '
                    f'at {item.warehouse_location}'
                )
        else:
            self.stdout.write(self.style.SUCCESS('✓ No low stock items'))
        
        # Expiring soon (within 30 days)
        expiry_date = timezone.now().date() + timedelta(days=30)
        expiring_items = Stock.objects.filter(
            expiry_alert_date__lte=expiry_date,
            expiry_alert_date__gte=timezone.now().date()
        )
        
        if expiring_items.exists():
            self.stdout.write(self.style.WARNING('\nEXPIRY ALERTS:'))
            for item in expiring_items:
                days_remaining = (item.expiry_alert_date - timezone.now().date()).days
                self.stdout.write(
                    f'  ⏰ {item.product.name} expires in {days_remaining} days '
                    f'({item.quantity_bags} bags at {item.warehouse_location})'
                )
        else:
            self.stdout.write(self.style.SUCCESS('✓ No items expiring soon'))
        
        # Already expired
        expired_items = Stock.objects.filter(expiry_alert_date__lt=timezone.now().date())
        
        if expired_items.exists():
            self.stdout.write(self.style.ERROR('\nEXPIRED ITEMS:'))
            for item in expired_items:
                self.stdout.write(
                    f'  ❌ {item.product.name} - EXPIRED on {item.expiry_alert_date} '
                    f'({item.quantity_bags} bags at {item.warehouse_location})'
                )
        else:
            self.stdout.write(self.style.SUCCESS('✓ No expired items'))
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Total stock items checked: {Stock.objects.count()}')
