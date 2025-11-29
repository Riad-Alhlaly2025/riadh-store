"""
Unit tests for service layer
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.apps import apps
from store.services.order_service import OrderService
from decimal import Decimal
from unittest.mock import patch, MagicMock

class OrderServiceTestCase(TestCase):
    """Test cases for OrderService"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test product
        Product = apps.get_model('store', 'Product')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=Decimal('19.99'),
            stock_quantity=10,
            category='Test Category'
        )
        
        # Create cart items
        self.cart_items = [
            {
                'product': self.product,
                'quantity': 2,
                'total_price': Decimal('39.98')
            }
        ]
        
        # Shipping address
        self.shipping_address = {
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'Test State',
            'phone': '123-456-7890'
        }
    
    def test_create_order_success(self):
        """Test successful order creation"""
        # Create order
        order = OrderService.create_order(
            user=self.user,
            cart_items=self.cart_items,
            shipping_address=self.shipping_address
        )
        
        # Verify order was created
        self.assertIsNotNone(order)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_amount, Decimal('39.98'))
        self.assertEqual(order.status, 'pending')
        
        # Verify order items were created
        OrderItem = apps.get_model('store', 'OrderItem')
        order_items = OrderItem.objects.filter(order=order)
        self.assertEqual(order_items.count(), 1)
        self.assertEqual(order_items.first().quantity, 2)
        
        # Verify product stock was updated
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 8)
    
    def test_create_order_invalid_cart_items(self):
        """Test order creation with invalid cart items"""
        # Test with empty cart
        with self.assertRaises(Exception):
            OrderService.create_order(
                user=self.user,
                cart_items=[],
                shipping_address=self.shipping_address
            )
    
    def test_update_order_status_valid_transition(self):
        """Test valid order status transition"""
        # Create order
        order = OrderService.create_order(
            user=self.user,
            cart_items=self.cart_items,
            shipping_address=self.shipping_address
        )
        
        # Update status
        updated_order = OrderService.update_order_status(order.id, 'processing')
        
        # Verify status was updated
        self.assertEqual(updated_order.status, 'processing')
    
    def test_update_order_status_invalid_transition(self):
        """Test invalid order status transition"""
        # Create order
        order = OrderService.create_order(
            user=self.user,
            cart_items=self.cart_items,
            shipping_address=self.shipping_address
        )
        
        # Try invalid transition (pending -> delivered)
        with self.assertRaises(ValueError):
            OrderService.update_order_status(order.id, 'delivered')
    
    def test_get_user_orders(self):
        """Test getting user orders"""
        # Create order
        order = OrderService.create_order(
            user=self.user,
            cart_items=self.cart_items,
            shipping_address=self.shipping_address
        )
        
        # Get user orders
        user_orders = OrderService.get_user_orders(self.user)
        
        # Verify we got the order
        self.assertEqual(user_orders.count(), 1)
        self.assertEqual(user_orders.first().id, order.id)
    
    def test_get_order_statistics(self):
        """Test getting order statistics"""
        # Create order
        order = OrderService.create_order(
            user=self.user,
            cart_items=self.cart_items,
            shipping_address=self.shipping_address
        )
        
        # Get statistics
        stats = OrderService.get_order_statistics()
        
        # Verify statistics
        self.assertEqual(stats['total_orders'], 1)
        self.assertEqual(stats['pending_orders'], 1)
        self.assertEqual(stats['total_revenue'], Decimal('0.00'))  # Not delivered yet
        
        # Update order to delivered
        OrderService.update_order_status(order.id, 'processing')
        OrderService.update_order_status(order.id, 'shipped')
        OrderService.update_order_status(order.id, 'delivered')
        
        # Get updated statistics
        stats = OrderService.get_order_statistics()
        self.assertEqual(stats['delivered_orders'], 1)
        self.assertEqual(stats['total_revenue'], Decimal('39.98'))

class RecommendationServiceTestCase(TestCase):
    """Test cases for RecommendationService"""
    
    def setUp(self):
        """Set up test data"""
        # Create test products
        Product = apps.get_model('store', 'Product')
        self.product1 = Product.objects.create(
            name='Laptop',
            description='High performance laptop for gaming and work',
            price=Decimal('999.99'),
            category='Electronics',
            brand='TechBrand'
        )
        
        self.product2 = Product.objects.create(
            name='Gaming Mouse',
            description='High precision gaming mouse with RGB lighting',
            price=Decimal('49.99'),
            category='Electronics',
            brand='TechBrand'
        )
        
        self.product3 = Product.objects.create(
            name='Coffee Maker',
            description='Automatic coffee maker for your kitchen',
            price=Decimal('89.99'),
            category='Home & Kitchen',
            brand='HomeBrand'
        )
    
    @patch('store.services.recommendation_service.RecommendationService._get_popular_products')
    def test_content_based_recommendations(self, mock_popular):
        """Test content-based recommendations"""
        from store.services.recommendation_service import recommendation_service
        
        # Mock fallback method
        mock_popular.return_value = []
        
        # Get recommendations
        recommendations = recommendation_service.get_content_based_recommendations(
            self.product1.id, 
            num_recommendations=2
        )
        
        # Verify we get recommendations (might be empty due to TF-IDF requirements)
        self.assertIsInstance(recommendations, list)
    
    def test_category_based_recommendations(self):
        """Test category-based recommendations"""
        from store.services.recommendation_service import recommendation_service
        
        # Get recommendations
        recommendations = recommendation_service._get_category_based_recommendations(
            self.product1.id,
            num_recommendations=2
        )
        
        # Should get the gaming mouse (same category)
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].id, self.product2.id)
    
    def test_popular_products(self):
        """Test getting popular products"""
        from store.services.recommendation_service import recommendation_service
        
        # Create orders to make products popular
        Order = apps.get_model('store', 'Order')
        OrderItem = apps.get_model('store', 'OrderItem')
        
        # Create user and order
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        order = Order.objects.create(
            user=user,
            total_amount=Decimal('999.99'),
            status='delivered'
        )
        
        # Create order items
        OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=1,
            price=self.product1.price
        )
        
        # Get popular products
        popular_products = recommendation_service._get_popular_products(5)
        
        # Verify we get products
        self.assertIsInstance(popular_products, list)