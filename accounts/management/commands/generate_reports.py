from django.core.management.base import BaseCommand
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from customers.models import Customer
from farmers.models import Farmer, FarmerSupply
from orders.models import Order
from inventory.models import Stock, StockMovement
from products.models import Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Generate comprehensive business reports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to include in report (default: 30)',
        )

    def handle(self, *args, **kwargs):
        days = kwargs['days']
        start_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write('='*70)
        self.stdout.write(self.style.SUCCESS(f'MAIZE SUPPLY & STORAGE ENTERPRISE - BUSINESS REPORT'))
        self.stdout.write(f'Report Period: Last {days} days ({start_date.date()} to {timezone.now().date()})')
        self.stdout.write('='*70)
        
        # Customer Statistics
        self.stdout.write('\n📊 CUSTOMER STATISTICS')
        self.stdout.write('-'*70)
        total_customers = Customer.objects.filter(is_active=True).count()
        new_customers = Customer.objects.filter(created_at__gte=start_date).count()
        self.stdout.write(f'Total Active Customers: {total_customers}')
        self.stdout.write(f'New Customers (last {days} days): {new_customers}')
        
        # Farmer Statistics
        self.stdout.write('\n🌾 FARMER STATISTICS')
        self.stdout.write('-'*70)
        total_farmers = Farmer.objects.filter(is_active=True).count()
        approved_farmers = Farmer.objects.filter(is_active=True, is_approved=True).count()
        pending_farmers = Farmer.objects.filter(is_active=True, is_approved=False).count()
        self.stdout.write(f'Total Active Farmers: {total_farmers}')
        self.stdout.write(f'Approved Farmers: {approved_farmers}')
        self.stdout.write(f'Pending Approval: {pending_farmers}')
        
        # Farmer Supply Summary
        supplies = FarmerSupply.objects.filter(date_delivered__gte=start_date)
        supply_stats = supplies.aggregate(
            total_bags=Sum('quantity_bags'),
            total_cost=Sum('total_cost'),
            total_paid=Sum('amount_paid'),
            count=Count('id')
        )
        
        self.stdout.write(f'\nFarmer Supplies (last {days} days):')
        self.stdout.write(f'  Total Supplies: {supply_stats["count"] or 0}')
        self.stdout.write(f'  Total Bags Received: {supply_stats["total_bags"] or 0}')
        self.stdout.write(f'  Total Cost: GHS {supply_stats["total_cost"] or 0:.2f}')
        self.stdout.write(f'  Total Paid: GHS {supply_stats["total_paid"] or 0:.2f}')
        outstanding = (supply_stats["total_cost"] or 0) - (supply_stats["total_paid"] or 0)
        self.stdout.write(self.style.WARNING(f'  Outstanding Payments: GHS {outstanding:.2f}'))
        
        # Stock Levels
        self.stdout.write('\n📦 STOCK LEVELS')
        self.stdout.write('-'*70)
        stock_summary = Stock.objects.aggregate(
            total_bags=Sum('quantity_bags'),
            total_tons=Sum('quantity_tons'),
            low_stock_count=Count('id', filter=Q(quantity_bags__lt=100))
        )
        self.stdout.write(f'Total Stock: {stock_summary["total_bags"] or 0} bags')
        self.stdout.write(f'Total Tons: {stock_summary["total_tons"] or 0:.3f} tons')
        if stock_summary["low_stock_count"] > 0:
            self.stdout.write(self.style.WARNING(f'Low Stock Items: {stock_summary["low_stock_count"]}'))
        
        # Product-wise stock
        self.stdout.write('\nStock by Product:')
        for product in Product.objects.all():
            product_stock = Stock.objects.filter(product=product).aggregate(
                total=Sum('quantity_bags')
            )['total'] or 0
            self.stdout.write(f'  {product.name}: {product_stock} bags')
        
        # Order Statistics
        self.stdout.write('\n🛒 ORDER STATISTICS')
        self.stdout.write('-'*70)
        orders = Order.objects.filter(created_at__gte=start_date)
        order_stats = orders.aggregate(
            total_orders=Count('id'),
            total_revenue=Sum('total_price', filter=Q(order_status='DELIVERED')),
            pending_orders=Count('id', filter=Q(order_status='PENDING')),
            processing_orders=Count('id', filter=Q(order_status='PROCESSING')),
            delivered_orders=Count('id', filter=Q(order_status='DELIVERED')),
            cancelled_orders=Count('id', filter=Q(order_status='CANCELLED')),
        )
        
        self.stdout.write(f'Total Orders (last {days} days): {order_stats["total_orders"] or 0}')
        self.stdout.write(f'  Pending: {order_stats["pending_orders"] or 0}')
        self.stdout.write(f'  Processing: {order_stats["processing_orders"] or 0}')
        self.stdout.write(f'  Delivered: {order_stats["delivered_orders"] or 0}')
        self.stdout.write(f'  Cancelled: {order_stats["cancelled_orders"] or 0}')
        self.stdout.write(self.style.SUCCESS(f'\nTotal Revenue (Delivered): GHS {order_stats["total_revenue"] or 0:.2f}'))
        
        # Top Products
        self.stdout.write('\n🏆 TOP SELLING PRODUCTS')
        self.stdout.write('-'*70)
        top_products = Order.objects.filter(
            created_at__gte=start_date,
            order_status='DELIVERED'
        ).values('product__name').annotate(
            total_sold=Sum('quantity_bags'),
            revenue=Sum('total_price')
        ).order_by('-total_sold')[:5]
        
        for i, item in enumerate(top_products, 1):
            self.stdout.write(
                f'{i}. {item["product__name"]}: {item["total_sold"]} bags - '
                f'GHS {item["revenue"]:.2f}'
            )
        
        # Stock Movements
        self.stdout.write('\n📈 STOCK MOVEMENTS')
        self.stdout.write('-'*70)
        movements = StockMovement.objects.filter(created_at__gte=start_date)
        movement_stats = movements.values('movement_type').annotate(
            count=Count('id'),
            total_bags=Sum('quantity_bags')
        )
        
        for stat in movement_stats:
            self.stdout.write(
                f'{stat["movement_type"]}: {stat["count"]} movements, '
                f'{stat["total_bags"]} bags'
            )
        
        # Financial Summary
        self.stdout.write('\n💰 FINANCIAL SUMMARY')
        self.stdout.write('-'*70)
        total_revenue = order_stats["total_revenue"] or 0
        total_supply_cost = supply_stats["total_cost"] or 0
        gross_profit = total_revenue - total_supply_cost
        
        self.stdout.write(f'Total Revenue: GHS {total_revenue:.2f}')
        self.stdout.write(f'Total Supply Costs: GHS {total_supply_cost:.2f}')
        if gross_profit > 0:
            self.stdout.write(self.style.SUCCESS(f'Gross Profit: GHS {gross_profit:.2f}'))
        else:
            self.stdout.write(self.style.WARNING(f'Gross Profit: GHS {gross_profit:.2f}'))
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('Report generated successfully!'))
