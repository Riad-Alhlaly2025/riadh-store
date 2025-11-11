import pytest
from django.contrib.auth.models import User
from decimal import Decimal
from django.apps import apps
from store.signals import get_commission_rate

@pytest.mark.django_db
class TestCommissionSystem:
    """Test commission calculation system"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data"""
        # Create users
        self.manager_user = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='testpass123'
        )
        self.seller_user = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='testpass123'
        )
        self.buyer_user = User.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='testpass123'
        )
        
        # Get models
        UserProfile = apps.get_model('store', 'UserProfile')
        Product = apps.get_model('store', 'Product')
        Order = apps.get_model('store', 'Order')
        OrderItem = apps.get_model('store', 'OrderItem')
        CommissionSettings = apps.get_model('store', 'CommissionSettings')
        
        # Update user profiles with roles
        self.manager_profile = UserProfile.objects.get(user=self.manager_user)
        self.manager_profile.role = 'manager'
        self.manager_profile.save()
        
        self.seller_profile = UserProfile.objects.get(user=self.seller_user)
        self.seller_profile.role = 'seller'
        self.seller_profile.save()
        
        self.buyer_profile = UserProfile.objects.get(user=self.buyer_user)
        self.buyer_profile.role = 'buyer'
        self.buyer_profile.save()
        
        # Create commission settings
        self.seller_commission_setting = CommissionSettings.objects.create(
            user_role='seller',
            product_category=None,  # General setting
            commission_rate=Decimal('10.00'),
            is_active=True
        )
        self.buyer_commission_setting = CommissionSettings.objects.create(
            user_role='buyer',
            product_category=None,  # General setting
            commission_rate=Decimal('2.00'),
            is_active=True
        )
        
        # Create products
        self.product1 = Product.objects.create(
            name='Test Product 1',
            price=Decimal('100.00'),
            description='Test product 1 description',
            seller=self.seller_user,
            category='phones'
        )
        self.product2 = Product.objects.create(
            name='Test Product 2',
            price=Decimal('50.00'),
            description='Test product 2 description',
            seller=self.seller_user,
            category='accessories'
        )
        
        # Create an order
        self.order = Order.objects.create(
            user=self.buyer_user,
            total_amount=Decimal('150.00'),
            shipping_address='Test Address',
            phone_number='123456789'
        )
        
        # Create order items
        self.order_item1 = OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            quantity=1,
            price=Decimal('100.00')
        )
        self.order_item2 = OrderItem.objects.create(
            order=self.order,
            product=self.product2,
            quantity=1,
            price=Decimal('50.00')
        )

    def test_get_commission_rate(self):
        """Test the get_commission_rate function"""
        # Test seller commission rate
        seller_rate = get_commission_rate('seller')
        assert seller_rate == Decimal('10.00')
        
        # Test buyer commission rate
        buyer_rate = get_commission_rate('buyer')
        assert buyer_rate == Decimal('2.00')
        
        # Test manager commission rate (should be 0.00 by default)
        manager_rate = get_commission_rate('manager')
        assert manager_rate == Decimal('0.00')

    def test_commission_calculation_on_delivery(self):
        """Test that commissions are calculated when order status changes to 'delivered'"""
        Commission = apps.get_model('store', 'Commission')
        
        # Initially, no commissions should exist
        assert Commission.objects.count() == 0
        
        # Change order status to 'delivered' to trigger commission calculation
        self.order.status = 'delivered'
        self.order.save()
        
        # Now commissions should be created
        commissions = Commission.objects.filter(order=self.order)
        assert commissions.count() == 2  # One for seller, one for buyer
        
        # Check seller commission
        seller_commission = commissions.get(user=self.seller_user)
        # Seller commission: 10% of (100 + 50) = 15.00
        assert seller_commission.amount == Decimal('15.00')
        assert seller_commission.rate == Decimal('10.00')
        assert seller_commission.is_paid == False
        
        # Check buyer commission
        buyer_commission = commissions.get(user=self.buyer_user)
        # Buyer commission: 2% of 150 = 3.00
        assert buyer_commission.amount == Decimal('3.00')
        assert buyer_commission.rate == Decimal('2.00')
        assert buyer_commission.is_paid == False

    def test_no_duplicate_commissions(self):
        """Test that commissions are not calculated twice for the same order"""
        Commission = apps.get_model('store', 'Commission')
        
        # Change order status to 'delivered' to trigger commission calculation
        self.order.status = 'delivered'
        self.order.save()
        
        # Check initial commission count
        initial_commission_count = Commission.objects.filter(order=self.order).count()
        assert initial_commission_count == 2
        
        # Change status to another value and back to 'delivered'
        self.order.status = 'processing'
        self.order.save()
        self.order.status = 'delivered'
        self.order.save()
        
        # Commission count should remain the same
        final_commission_count = Commission.objects.filter(order=self.order).count()
        assert final_commission_count == 2