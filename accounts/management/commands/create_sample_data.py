from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from customers.models import Customer
from farmers.models import Farmer, FarmerSupply
from products.models import Product
from pricing.models import Price
from inventory.models import Stock
from orders.models import Order
from blog.models import BlogPost
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates sample data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@maizesupply.com',
                password='admin123',
                first_name='System',
                last_name='Administrator',
                mobile_number='+233200000000',
                user_type='ADMIN'
            )
            self.stdout.write(self.style.SUCCESS('✓ Admin user created'))
        else:
            admin = User.objects.get(username='admin')
            self.stdout.write('✓ Admin user already exists')
        
        # Create staff user
        if not User.objects.filter(username='staff').exists():
            staff = User.objects.create_user(
                username='staff',
                email='staff@maizesupply.com',
                password='staff123',
                first_name='Staff',
                last_name='Member',
                mobile_number='+233200000001',
                user_type='STAFF'
            )
            self.stdout.write(self.style.SUCCESS('✓ Staff user created'))
        else:
            staff = User.objects.get(username='staff')
        
        # Create sample customers
        customer_data = [
            ('john_doe', 'John', 'Doe', '+233244123456', 'Accra'),
            ('jane_smith', 'Jane', 'Smith', '+233244123457', 'Kumasi'),
            ('kofi_mensah', 'Kofi', 'Mensah', '+233244123458', 'Tamale'),
        ]
        
        for username, first, last, phone, location in customer_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='password123',
                    first_name=first,
                    last_name=last,
                    mobile_number=phone,
                    user_type='CUSTOMER'
                )
                customer = Customer.objects.get(user=user)
                customer.location = location
                customer.save()
                self.stdout.write(f'✓ Customer {username} created')
        
        # Create products
        products_data = [
            ('Yellow Maize', 'Premium quality yellow maize', ['50kg bag', '100kg bag', '1 ton']),
            ('White Maize', 'High-quality white maize', ['50kg bag', '100kg bag', '1 ton']),
            ('Mixed Maize', 'Yellow and white maize mix', ['50kg bag', '100kg bag']),
        ]
        
        for name, desc, sizes in products_data:
            if not Product.objects.filter(name=name).exists():
                product = Product.objects.create(
                    name=name,
                    description=desc,
                    packaging_sizes=sizes,
                    is_available=True
                )
                
                # Create prices for each packaging size
                for size in sizes:
                    if '50kg' in size:
                        Price.objects.create(
                            product=product,
                            price_per_bag=Decimal('250.00'),
                            price_per_ton=Decimal('5000.00'),
                            packaging_size=size,
                            market_notes='Standard market price',
                            updated_by=admin,
                            is_current=True
                        )
                    elif '100kg' in size:
                        Price.objects.create(
                            product=product,
                            price_per_bag=Decimal('480.00'),
                            price_per_ton=Decimal('4800.00'),
                            packaging_size=size,
                            market_notes='Bulk pricing',
                            updated_by=admin,
                            is_current=True
                        )
                
                self.stdout.write(f'✓ Product {name} created with prices')
        
        # Create farmers
        farmers_data = [
            ('Kwame Asante', '+233501234567', 'GHA-123456789-0', 6.6884, -1.6234, 'Ashanti', 'Ejisu', 'Bonwire'),
            ('Ama Owusu', '+233501234568', 'GHA-123456789-1', 5.6037, -0.1870, 'Greater Accra', 'Tema', 'Afienya'),
            ('Kofi Adjei', '+233501234569', 'GHA-123456789-2', 9.4034, -0.8424, 'Northern', 'Tamale', 'Nyohini'),
        ]
        
        for name, phone, ghana_card, lat, lon, region, district, community in farmers_data:
            if not Farmer.objects.filter(ghana_card_number=ghana_card).exists():
                farmer = Farmer.objects.create(
                    full_name=name,
                    mobile_number=phone,
                    ghana_card_number=ghana_card,
                    gps_latitude=Decimal(str(lat)),
                    gps_longitude=Decimal(str(lon)),
                    region=region,
                    district=district,
                    community=community,
                    maize_types_supplied=['Yellow Maize', 'White Maize'],
                    is_approved=True,
                    is_active=True,
                    created_by=admin
                )
                self.stdout.write(f'✓ Farmer {name} created')
        
        # Create stock
        products = Product.objects.all()
        farmers = Farmer.objects.filter(is_approved=True)
        
        for product in products:
            if not Stock.objects.filter(product=product).exists():
                for i in range(2):
                    Stock.objects.create(
                        product=product,
                        quantity_bags=random.randint(100, 500),
                        quantity_tons=Decimal(str(random.uniform(5, 25))),
                        source_type='FARMER' if i == 0 else 'MARKET_PURCHASE',
                        farmer=random.choice(farmers) if i == 0 else None,
                        quality_grade='Premium' if i == 0 else 'Standard',
                        moisture_content=Decimal('13.5'),
                        warehouse_location=f'Warehouse {random.choice(["A", "B", "C"])}',
                        cost_price=Decimal('230.00'),
                        date_received=timezone.now() - timedelta(days=random.randint(1, 30)),
                        expiry_alert_date=timezone.now().date() + timedelta(days=random.randint(60, 180))
                    )
                self.stdout.write(f'✓ Stock created for {product.name}')
        
        # Create blog posts
        blog_posts_data = [
            ('Understanding Maize Storage', 'Tips for properly storing maize', 'Storage Tips'),
            ('Maize Market Trends 2025', 'Latest market analysis and predictions', 'Market Analysis'),
            ('Best Practices for Maize Farmers', 'Guide for maize farmers', 'Farming Tips'),
        ]
        
        for title, content, category in blog_posts_data:
            if not BlogPost.objects.filter(title=title).exists():
                BlogPost.objects.create(
                    title=title,
                    content=content * 10,  # Repeat for longer content
                    category=category,
                    is_published=True,
                    author=admin,
                    published_at=timezone.now()
                )
                self.stdout.write(f'✓ Blog post "{title}" created')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sample data created successfully!'))
        self.stdout.write(self.style.SUCCESS('\nLogin credentials:'))
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Staff: staff / staff123')
        self.stdout.write('Customer: john_doe / password123')
