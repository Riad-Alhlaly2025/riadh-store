from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.apps import apps
from decimal import Decimal

class Command(BaseCommand):
    help = 'Demonstrate the complete commission system'

    def handle(self, *args, **options):
        # Import models dynamically
        Product = apps.get_model('store', 'Product')
        Order = apps.get_model('store', 'Order')
        OrderItem = apps.get_model('store', 'OrderItem')
        Commission = apps.get_model('store', 'Commission')
        UserProfile = apps.get_model('store', 'UserProfile')
        CommissionSettings = apps.get_model('store', 'CommissionSettings')
        
        self.stdout.write("=== Demonstrating Complete Commission System ===\n")
        
        # 1. Show commission settings
        self.stdout.write("1. Current Commission Settings:")
        settings = CommissionSettings.objects.all()
        for setting in settings:
            category = setting.product_category if setting.product_category else "الكل"
            self.stdout.write(f"   - {setting.get_user_role_display()}: {category} -> {setting.commission_rate}%")
        
        # 2. Create test users
        self.stdout.write("\n2. Creating Test Users:")
        
        # Create seller 1
        seller1, created = User.objects.get_or_create(
            username='seller1',
            defaults={
                'email': 'seller1@test.com',
                'first_name': 'Seller',
                'last_name': 'One'
            }
        )
        if created:
            seller1.set_password('testpass123')
            seller1.save()
        
        seller1_profile, created = UserProfile.objects.get_or_create(user=seller1)
        seller1_profile.role = 'seller'
        seller1_profile.save()
        
        # Create seller 2
        seller2, created = User.objects.get_or_create(
            username='seller2',
            defaults={
                'email': 'seller2@test.com',
                'first_name': 'Seller',
                'last_name': 'Two'
            }
        )
        if created:
            seller2.set_password('testpass123')
            seller2.save()
        
        seller2_profile, created = UserProfile.objects.get_or_create(user=seller2)
        seller2_profile.role = 'seller'
        seller2_profile.save()
        
        # Create buyer
        buyer, created = User.objects.get_or_create(
            username='buyer1',
            defaults={
                'email': 'buyer1@test.com',
                'first_name': 'Buyer',
                'last_name': 'One'
            }
        )
        if created:
            buyer.set_password('testpass123')
            buyer.save()
        
        buyer_profile, created = UserProfile.objects.get_or_create(user=buyer)
        buyer_profile.role = 'buyer'
        buyer_profile.save()
        
        self.stdout.write("   - Created sellers: seller1, seller2")
        self.stdout.write("   - Created buyer: buyer1")
        
        # 3. Create products with different sellers and categories
        self.stdout.write("\n3. Creating Test Products:")
        
        # Phone product by seller1
        phone_product, created = Product.objects.get_or_create(
            name='iPhone 15 Pro',
            defaults={
                'price': Decimal('4000.00'),
                'description': 'Apple iPhone 15 Pro - 256GB',
                'seller': seller1,
                'category': 'phones'
            }
        )
        
        # Computer product by seller2
        computer_product, created = Product.objects.get_or_create(
            name='MacBook Pro',
            defaults={
                'price': Decimal('8000.00'),
                'description': 'Apple MacBook Pro 16" - M3 Max',
                'seller': seller2,
                'category': 'computers'
            }
        )
        
        # Accessory product by seller1
        accessory_product, created = Product.objects.get_or_create(
            name='AirPods Pro',
            defaults={
                'price': Decimal('1000.00'),
                'description': 'Apple AirPods Pro 2nd Generation',
                'seller': seller1,
                'category': 'accessories'
            }
        )
        
        self.stdout.write("   - iPhone 15 Pro (phones) by seller1")
        self.stdout.write("   - MacBook Pro (computers) by seller2")
        self.stdout.write("   - AirPods Pro (accessories) by seller1")
        
        # 4. Create order
        self.stdout.write("\n4. Creating Order:")
        
        order, created = Order.objects.get_or_create(
            user=buyer,
            defaults={
                'status': 'pending',
                'total_amount': Decimal('13000.00'),
                'shipping_address': 'Riyadh, Saudi Arabia',
                'phone_number': '0501234567',
            }
        )
        
        if not created:
            order.status = 'pending'
            order.total_amount = Decimal('13000.00')
            order.save()
        
        self.stdout.write(f"   - Order #{order.id} created for buyer1")
        
        # 5. Create order items
        self.stdout.write("\n5. Adding Items to Order:")
        
        # Clear existing items
        OrderItem.objects.filter(order=order).delete()
        
        # Add phone
        OrderItem.objects.create(
            order=order,
            product=phone_product,
            quantity=1,
            price=phone_product.price
        )
        self.stdout.write("   - Added 1x iPhone 15 Pro")
        
        # Add computer
        OrderItem.objects.create(
            order=order,
            product=computer_product,
            quantity=1,
            price=computer_product.price
        )
        self.stdout.write("   - Added 1x MacBook Pro")
        
        # Add accessory
        OrderItem.objects.create(
            order=order,
            product=accessory_product,
            quantity=2,
            price=accessory_product.price
        )
        self.stdout.write("   - Added 2x AirPods Pro")
        
        # 6. Complete order to trigger commission calculation
        self.stdout.write("\n6. Completing Order (Triggering Commission Calculation):")
        order.status = 'delivered'
        order.save()
        self.stdout.write(f"   - Order #{order.id} marked as delivered")
        
        # 7. Show calculated commissions
        self.stdout.write("\n7. Calculated Commissions:")
        commissions = Commission.objects.filter(order=order)
        
        if commissions.exists():
            total_commission = Decimal('0.00')
            for commission in commissions:
                total_commission += commission.amount
                self.stdout.write(f"   - {commission.user.username}: {commission.amount} R.S ({commission.rate}%)")
            self.stdout.write(f"   - Total Commissions: {total_commission} R.S")
        else:
            self.stdout.write("   - No commissions calculated")
        
        self.stdout.write("\n=== Demonstration Complete ===")