from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from django.apps import apps
from django.http import HttpResponse

class PaymentTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Get models dynamically
        Product = apps.get_model('store', 'Product')
        Order = apps.get_model('store', 'Order')
        OrderItem = apps.get_model('store', 'OrderItem')
        Payment = apps.get_model('store', 'Payment')
        
        # Create a product
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('100.00'),
            description='Test product description'
        )
        
        # Create an order
        self.order = Order.objects.create(
            user=self.user,
            total_amount=Decimal('100.00'),
            shipping_address='Test Address',
            phone_number='123456789'
        )
        
        # Create an order item
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=Decimal('100.00')
        )

    def test_payment_creation(self):
        """Test that a payment can be created for an order"""
        Payment = apps.get_model('store', 'Payment')
        
        payment = Payment.objects.create(
            order=self.order,
            payment_method='stripe',
            transaction_id='test_transaction_id',
            amount=Decimal('100.00'),
            currency='USD',
            status='pending'
        )
        
        self.assertEqual(payment.order, self.order)
        self.assertEqual(payment.payment_method, 'stripe')
        self.assertEqual(payment.amount, Decimal('100.00'))
        self.assertEqual(payment.status, 'pending')

    def test_payment_str_representation(self):
        """Test the string representation of a payment"""
        Payment = apps.get_model('store', 'Payment')
        
        payment = Payment.objects.create(
            order=self.order,
            payment_method='stripe',
            transaction_id='test_transaction_id',
            amount=Decimal('100.00'),
            currency='USD',
            status='completed'
        )
        
        expected_str = f"دفعة #{payment.pk} - طلب #{self.order.pk} - مكتمل"
        self.assertEqual(str(payment), expected_str)


# New tests for commission calculation system
class CommissionTestCase(TestCase):
    def setUp(self):
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
        
        # Get models dynamically
        UserProfile = apps.get_model('store', 'UserProfile')
        Product = apps.get_model('store', 'Product')
        Order = apps.get_model('store', 'Order')
        OrderItem = apps.get_model('store', 'OrderItem')
        CommissionSettings = apps.get_model('store', 'CommissionSettings')
        
        # Wait for user profiles to be created by signals
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
        from store.signals import get_commission_rate
        
        # Test seller commission rate
        seller_rate = get_commission_rate('seller')
        self.assertEqual(seller_rate, Decimal('10.00'))
        
        # Test buyer commission rate
        buyer_rate = get_commission_rate('buyer')
        self.assertEqual(buyer_rate, Decimal('2.00'))
        
        # Test manager commission rate (should be 0.00 by default)
        manager_rate = get_commission_rate('manager')
        self.assertEqual(manager_rate, Decimal('0.00'))

    def test_commission_calculation_on_delivery(self):
        """Test that commissions are calculated when order status changes to 'delivered'"""
        Commission = apps.get_model('store', 'Commission')
        
        # Initially, no commissions should exist
        self.assertEqual(Commission.objects.count(), 0)
        
        # Change order status to 'delivered' to trigger commission calculation
        self.order.status = 'delivered'
        self.order.save()
        
        # Now commissions should be created
        commissions = Commission.objects.filter(order=self.order)
        self.assertEqual(commissions.count(), 2)  # One for seller, one for buyer
        
        # Check seller commission
        seller_commission = commissions.get(user=self.seller_user)
        # Seller commission: 10% of (100 + 50) = 15.00
        self.assertEqual(seller_commission.amount, Decimal('15.00'))
        self.assertEqual(seller_commission.rate, Decimal('10.00'))
        self.assertFalse(seller_commission.is_paid)
        
        # Check buyer commission
        buyer_commission = commissions.get(user=self.buyer_user)
        # Buyer commission: 2% of 150 = 3.00
        self.assertEqual(buyer_commission.amount, Decimal('3.00'))
        self.assertEqual(buyer_commission.rate, Decimal('2.00'))
        self.assertFalse(buyer_commission.is_paid)

    def test_no_duplicate_commissions(self):
        """Test that commissions are not calculated twice for the same order"""
        Commission = apps.get_model('store', 'Commission')
        
        # Change order status to 'delivered' to trigger commission calculation
        self.order.status = 'delivered'
        self.order.save()
        
        # Check initial commission count
        initial_commission_count = Commission.objects.filter(order=self.order).count()
        self.assertEqual(initial_commission_count, 2)
        
        # Change status to another value and back to 'delivered'
        self.order.status = 'processing'
        self.order.save()
        self.order.status = 'delivered'
        self.order.save()
        
        # Commission count should remain the same
        final_commission_count = Commission.objects.filter(order=self.order).count()
        self.assertEqual(final_commission_count, 2)


class WebhookSecurityTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Get models dynamically
        Product = apps.get_model('store', 'Product')
        Order = apps.get_model('store', 'Order')
        OrderItem = apps.get_model('store', 'OrderItem')
        Payment = apps.get_model('store', 'Payment')
        
        # Create a product
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('100.00'),
            description='Test product description'
        )
        
        # Create an order
        self.order = Order.objects.create(
            user=self.user,
            total_amount=Decimal('100.00'),
            shipping_address='Test Address',
            phone_number='123456789'
        )
        
        # Create an order item
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=Decimal('100.00')
        )
        
        # Create a payment
        self.payment = Payment.objects.create(
            order=self.order,
            payment_method='stripe',
            transaction_id='test_transaction_id',
            amount=Decimal('100.00'),
            currency='USD',
            status='pending'
        )

    def test_stripe_webhook_invalid_signature(self):
        """Test that stripe webhook rejects invalid signatures"""
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        
        # Send request with invalid signature
        response = client.post(
            reverse('stripe_webhook'),
            data='{"type": "payment_intent.succeeded"}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='invalid_signature'
        )
        
        # Should return 400 for invalid signature
        self.assertEqual(response.status_code, 400)  # type: ignore

    def test_stripe_webhook_missing_signature(self):
        """Test that stripe webhook rejects missing signatures"""
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        
        # Send request without signature header
        response = client.post(
            reverse('stripe_webhook'),
            data='{"type": "payment_intent.succeeded"}',
            content_type='application/json'
        )
        
        # Should return 403 for missing signature
        self.assertEqual(response.status_code, 403)  # type: ignore