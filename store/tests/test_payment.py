import pytest
from django.contrib.auth.models import User
from decimal import Decimal
from django.apps import apps

@pytest.mark.django_db
class TestPaymentSystem:
    """Test payment system functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data"""
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Get models
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
        
        assert payment.order == self.order
        assert payment.payment_method == 'stripe'
        assert payment.amount == Decimal('100.00')
        assert payment.status == 'pending'

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
        assert str(payment) == expected_str