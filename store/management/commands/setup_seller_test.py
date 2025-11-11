from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.apps import apps

class Command(BaseCommand):
    help = 'Setup test data for seller functionalities'

    def handle(self, *args, **options):
        # Import models dynamically
        UserProfile = apps.get_model('store', 'UserProfile')
        Product = apps.get_model('store', 'Product')
        
        # Get or create test seller
        user, created = User.objects.get_or_create(
            username='test_seller',
            defaults={
                'email': 'seller@test.com',
                'first_name': 'Test',
                'last_name': 'Seller'
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
        
        # Ensure user has seller profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = 'seller'
        profile.save()
        
        # Create test products
        Product.objects.get_or_create(
            name='iPhone 15',
            defaults={
                'price': 4000,
                'description': 'Apple iPhone 15',
                'category': 'phones',
                'seller': user
            }
        )
        
        Product.objects.get_or_create(
            name='MacBook Pro',
            defaults={
                'price': 8000,
                'description': 'Apple MacBook Pro 16"',
                'category': 'computers',
                'seller': user
            }
        )
        
        self.stdout.write(
            f'Successfully setup test seller "{user.username}" with 2 products'
        )