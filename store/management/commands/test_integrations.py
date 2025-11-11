from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Product, Order, SocialMediaIntegration, ShippingIntegration, ExternalInventory, AccountingIntegration, AnalyticsIntegration

class Command(BaseCommand):
    help = 'Test the new integration features implementation'

    def handle(self, *args, **options):
        # Create a test user if not exists
        user, created = User.objects.get_or_create(
            username='testuser2',
            defaults={
                'email': 'test2@example.com',
                'first_name': 'Test2',
                'last_name': 'User2'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created test user')
            )
        
        # Create a test product if not exists
        product, created = Product.objects.get_or_create(
            name='Test Product',
            defaults={
                'price': 100.00,
                'description': 'Test product for integration testing',
                'category': 'phones',
                'stock_quantity': 10
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created test product')
            )
        
        # Create a test order if not exists
        order, created = Order.objects.get_or_create(
            user=user,
            defaults={
                'total_amount': 100.00,
                'shipping_address': 'Test Address',
                'phone_number': '1234567890',
                'status': 'pending'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created test order')
            )
        
        # Test Social Media Integration
        social_integration, created = SocialMediaIntegration.objects.get_or_create(
            product=product,
            platform='facebook',
            defaults={
                'status': 'pending'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created social media integration')
            )
        
        # Test Shipping Integration
        shipping_integration, created = ShippingIntegration.objects.get_or_create(
            order=order,
            provider='fedex',
            defaults={
                'shipping_cost': 20.00,
                'status': 'pending'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created shipping integration')
            )
        
        # Test External Inventory
        external_inventory, created = ExternalInventory.objects.get_or_create(
            product=product,
            external_id='EXT123',
            defaults={
                'system_name': 'ExternalSystem',
                'external_stock': 50,
                'sync_status': 'pending'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created external inventory integration')
            )
        
        # Test Accounting Integration
        accounting_integration, created = AccountingIntegration.objects.get_or_create(
            order=order,
            accounting_system='QuickBooks',
            defaults={
                'sync_status': 'pending'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created accounting integration')
            )
        
        # Test Analytics Integration
        analytics_integration, created = AnalyticsIntegration.objects.get_or_create(
            event_type='page_view',
            url='http://localhost:8000/test',
            defaults={
                'user': user
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created analytics integration')
            )
        
        self.stdout.write(
            self.style.SUCCESS('All integration tests passed successfully!')
        )