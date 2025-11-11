from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Product, Order, OrderItem, SocialMediaIntegration, ShippingIntegration, ExternalInventory, AccountingIntegration, AnalyticsIntegration
from decimal import Decimal
import random
from datetime import datetime

class Command(BaseCommand):
    help = 'Demonstrate the integration features in a real scenario'

    def handle(self, *args, **options):
        # Create test users
        seller_user, _ = User.objects.get_or_create(
            username='seller_demo',
            defaults={
                'email': 'seller@demo.com',
                'first_name': 'Seller',
                'last_name': 'Demo'
            }
        )
        
        buyer_user, _ = User.objects.get_or_create(
            username='buyer_demo',
            defaults={
                'email': 'buyer@demo.com',
                'first_name': 'Buyer',
                'last_name': 'Demo'
            }
        )
        
        self.stdout.write('Created demo users')
        
        # Create test products
        products_data = [
            {'name': 'iPhone 15 Pro', 'price': Decimal('4500.00'), 'category': 'phones', 'stock_quantity': 25},
            {'name': 'Samsung Galaxy S24', 'price': Decimal('3800.00'), 'category': 'phones', 'stock_quantity': 30},
            {'name': 'MacBook Pro 16"', 'price': Decimal('8500.00'), 'category': 'computers', 'stock_quantity': 15},
            {'name': 'Dell XPS 15', 'price': Decimal('6500.00'), 'category': 'computers', 'stock_quantity': 20},
            {'name': 'AirPods Pro', 'price': Decimal('1200.00'), 'category': 'accessories', 'stock_quantity': 50},
        ]
        
        products = []
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            products.append(product)
            
        self.stdout.write('Created demo products')
        
        # Create a test order
        order = Order.objects.create(
            user=buyer_user,
            total_amount=Decimal('4500.00'),
            shipping_address='Riyadh, Saudi Arabia',
            phone_number='1234567890',
            status='processing'
        )
        
        # Create order items
        OrderItem.objects.create(
            order=order,
            product=products[0],  # iPhone 15 Pro
            quantity=1,
            price=Decimal('4500.00')
        )
        
        self.stdout.write('Created demo order')
        
        # Demonstrate Social Media Integration
        social_platforms = ['facebook', 'twitter', 'instagram', 'linkedin']
        for product in products:
            platform = random.choice(social_platforms)
            SocialMediaIntegration.objects.create(
                product=product,
                platform=platform,
                status='posted',
                post_id=f'post_{random.randint(1000, 9999)}'
            )
            
        self.stdout.write('Demonstrated social media integration')
        
        # Demonstrate Shipping Integration
        shipping_providers = ['fedex', 'dhl', 'ups']
        ShippingIntegration.objects.create(
            order=order,
            provider=random.choice(shipping_providers),
            tracking_number=f'TRACK{random.randint(100000, 999999)}',
            shipping_cost=Decimal('75.00'),
            status='shipped',
            estimated_delivery=datetime.now()
        )
        
        self.stdout.write('Demonstrated shipping integration')
        
        # Demonstrate External Inventory Integration
        external_systems = ['ERPNext', 'Odoo', 'SAP']
        for product in products:
            ExternalInventory.objects.create(
                product=product,
                external_id=f'EXT{random.randint(1000, 9999)}',
                system_name=random.choice(external_systems),
                external_stock=random.randint(10, 100),
                sync_status='synced',
                last_synced=datetime.now()
            )
            
        self.stdout.write('Demonstrated external inventory integration')
        
        # Demonstrate Accounting Integration
        accounting_systems = ['QuickBooks', 'Xero', 'FreshBooks']
        AccountingIntegration.objects.create(
            order=order,
            accounting_system=random.choice(accounting_systems),
            transaction_id=f'TXN{random.randint(100000, 999999)}',
            sync_status='synced',
            synced_at=datetime.now()
        )
        
        self.stdout.write('Demonstrated accounting integration')
        
        # Demonstrate Analytics Integration
        event_types = ['page_view', 'product_view', 'add_to_cart', 'checkout', 'purchase']
        for i in range(20):
            AnalyticsIntegration.objects.create(
                event_type=random.choice(event_types),
                user=random.choice([seller_user, buyer_user]) if random.choice([True, False]) else None,
                session_key=f'session_{random.randint(1000, 9999)}' if random.choice([True, False]) else None,
                product=random.choice(products) if random.choice([True, False]) else None,
                order=order if random.choice([True, False]) else None,
                url='https://demo-store.com/product/1/',
                referrer='https://google.com' if random.choice([True, False]) else 'https://facebook.com',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                ip_address=f'192.168.{random.randint(0, 255)}.{random.randint(0, 255)}'
            )
            
        self.stdout.write('Demonstrated analytics integration')
        
        self.stdout.write(
            self.style.SUCCESS('All integration features demonstrated successfully!')
        )
        
        # Print summary
        self.stdout.write('\n=== Integration Summary ===')
        self.stdout.write(f'Social Media Posts: {SocialMediaIntegration.objects.count()}')
        self.stdout.write(f'Shipping Integrations: {ShippingIntegration.objects.count()}')
        self.stdout.write(f'External Inventory Links: {ExternalInventory.objects.count()}')
        self.stdout.write(f'Accounting Integrations: {AccountingIntegration.objects.count()}')
        self.stdout.write(f'Analytics Events: {AnalyticsIntegration.objects.count()}')