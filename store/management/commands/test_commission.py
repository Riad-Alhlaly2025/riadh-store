from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.apps import apps
from decimal import Decimal

class Command(BaseCommand):
    help = 'Test commission calculation system'

    def add_arguments(self, parser):
        parser.add_argument('--role', type=str, default='seller', help='User role to test (seller or buyer)')

    def handle(self, *args, **options):
        # Import models dynamically
        Product = apps.get_model('store', 'Product')
        Order = apps.get_model('store', 'Order')
        OrderItem = apps.get_model('store', 'OrderItem')
        Commission = apps.get_model('store', 'Commission')
        UserProfile = apps.get_model('store', 'UserProfile')
        
        role = options['role']
        
        # Create test seller user
        seller, created = User.objects.get_or_create(
            username='test_seller',
            defaults={
                'email': 'seller@test.com',
                'first_name': 'Test',
                'last_name': 'Seller'
            }
        )
        
        if created:
            seller.set_password('testpass123')
            seller.save()
        
        # Ensure seller has a profile with seller role
        seller_profile, created = UserProfile.objects.get_or_create(user=seller)
        seller_profile.role = 'seller'
        seller_profile.save()
        
        # Create test buyer user
        buyer, created = User.objects.get_or_create(
            username='test_buyer',
            defaults={
                'email': 'buyer@test.com',
                'first_name': 'Test',
                'last_name': 'Buyer'
            }
        )
        
        if created:
            buyer.set_password('testpass123')
            buyer.save()
        
        # Ensure buyer has a profile with buyer role
        buyer_profile, created = UserProfile.objects.get_or_create(user=buyer)
        buyer_profile.role = 'buyer'
        buyer_profile.save()
        
        # Create test products with seller assigned
        product1, created = Product.objects.get_or_create(
            name='Test Product 1 for Commission',
            defaults={
                'price': Decimal('100.00'),
                'description': 'Test product 1 for commission calculation',
                'seller': seller,
                'category': 'phones'
            }
        )
        
        product2, created = Product.objects.get_or_create(
            name='Test Product 2 for Commission',
            defaults={
                'price': Decimal('50.00'),
                'description': 'Test product 2 for commission calculation',
                'seller': seller,
                'category': 'accessories'
            }
        )
        
        # Create or get test order with pending status
        order, created = Order.objects.get_or_create(
            user=buyer,
            defaults={
                'status': 'pending',  # Start with pending status
                'total_amount': Decimal('150.00'),
                'shipping_address': 'Test Address',
                'phone_number': '1234567890',
            }
        )
        
        # If order already exists, reset its status to pending
        if not created:
            order.status = 'pending'
            order.save()
        
        # Create order items if not exists
        order_item1, created = OrderItem.objects.get_or_create(
            order=order,
            product=product1,
            quantity=1,
            defaults={
                'price': Decimal('100.00')
            }
        )
        
        order_item2, created = OrderItem.objects.get_or_create(
            order=order,
            product=product2,
            quantity=1,
            defaults={
                'price': Decimal('50.00')
            }
        )
        
        # Update order status to 'delivered' to trigger commission calculation
        original_status = order.status
        order.status = 'delivered'
        order.save()
        
        # Check if commissions were created
        commissions = Commission.objects.filter(order=order)
        
        if commissions.exists():
            self.stdout.write(
                f'Successfully calculated {commissions.count()} commissions for order #{order.pk}:'
            )
            for commission in commissions:
                self.stdout.write(
                    f'- User: {commission.user.username}, Amount: {commission.amount} R.S, Rate: {commission.rate}%'
                )
        else:
            self.stdout.write(
                f'No commissions were calculated. Order status changed from {original_status} to {order.status}'
            )