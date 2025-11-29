"""
Unit tests for shipping integration functionality
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.apps import apps
from django.urls import reverse
from decimal import Decimal
from unittest.mock import patch, MagicMock
import json

class ShippingIntegrationTestCase(TestCase):
    """Test cases for ShippingIntegration model and service"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user (buyer)
        self.buyer = User.objects.create_user(
            username='testbuyer',
            email='buyer@example.com',
            password='testpass123'
        )
        
        # Create test seller
        self.seller = User.objects.create_user(
            username='testseller',
            email='seller@example.com',
            password='testpass123'
        )
        
        # Create test product
        Product = apps.get_model('store', 'Product')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=Decimal('29.99'),
            stock_quantity=5,
            category='Electronics',
            seller=self.seller
        )
        
        # Create test order
        Order = apps.get_model('store', 'Order')
        self.order = Order.objects.create(
            user=self.buyer,
            total_amount=Decimal('29.99'),
            shipping_address='123 Test St, Test City',
            phone_number='123-456-7890',
            status='pending'
        )
        
        # Create order item
        OrderItem = apps.get_model('store', 'OrderItem')
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=Decimal('29.99')
        )
        
        # Get ShippingIntegration model
        self.ShippingIntegration = apps.get_model('store', 'ShippingIntegration')
    
    def test_shipping_integration_creation(self):
        """Test creating a shipping integration"""
        # Create shipping integration
        integration = self.ShippingIntegration.objects.create(
            order=self.order,
            provider='fedex',
            tracking_number='FEDEX123456789',
            shipping_cost=Decimal('15.99'),
            status='pending'
        )
        
        # Verify integration was created
        self.assertIsNotNone(integration.id)
        self.assertEqual(integration.order, self.order)
        self.assertEqual(integration.provider, 'fedex')
        self.assertEqual(integration.tracking_number, 'FEDEX123456789')
        self.assertEqual(integration.shipping_cost, Decimal('15.99'))
        self.assertEqual(integration.status, 'pending')
    
    def test_shipping_integration_str_representation(self):
        """Test string representation of shipping integration"""
        integration = self.ShippingIntegration.objects.create(
            order=self.order,
            provider='dhl',
            status='shipped'
        )
        
        expected_str = f"Shipment for Order #{self.order.id} via dhl"
        self.assertEqual(str(integration), expected_str)
    
    def test_get_shipped_orders(self):
        """Test getting shipped orders"""
        # Create multiple integrations with different statuses
        self.ShippingIntegration.objects.create(
            order=self.order,
            provider='fedex',
            status='pending'
        )
        
        order2 = Order.objects.create(
            user=self.buyer,
            total_amount=Decimal('49.99'),
            shipping_address='456 Test Ave, Test City',
            phone_number='987-654-3210',
            status='processing'
        )
        
        self.ShippingIntegration.objects.create(
            order=order2,
            provider='dhl',
            status='shipped',
            tracking_number='DHL987654321'
        )
        
        # Test filtering by status
        shipped = self.ShippingIntegration.objects.filter(status='shipped')
        self.assertEqual(shipped.count(), 1)
        self.assertEqual(shipped.first().tracking_number, 'DHL987654321')
    
    @patch('store.services.shipping_service.ShippingService.create_fedex_shipment')
    def test_fedex_shipment_creation_success(self, mock_create):
        """Test successful FedEx shipment creation"""
        # Mock successful FedEx shipment creation
        mock_create.return_value = {
            'success': True,
            'tracking_number': 'FEDEX_TEST_12345',
            'label_url': 'https://fedex.com/label/12345',
            'cost': Decimal('12.50')
        }
        
        # Create integration
        integration = self.ShippingIntegration.objects.create(
            order=self.order,
            provider='fedex',
            status='pending'
        )
        
        # Call the service method
        from store.services.shipping_service import ShippingService
        result = ShippingService.create_fedex_shipment(integration.id)
        
        # Verify the result
        self.assertTrue(result['success'])
        self.assertEqual(result['tracking_number'], 'FEDEX_TEST_12345')
        
        # Verify integration was updated
        integration.refresh_from_db()
        self.assertEqual(integration.status, 'shipped')
        self.assertEqual(integration.tracking_number, 'FEDEX_TEST_12345')
        self.assertEqual(integration.shipping_cost, Decimal('12.50'))
    
    @patch('store.services.shipping_service.ShippingService.create_dhl_shipment')
    def test_dhl_shipment_creation_failure(self, mock_create):
        """Test failed DHL shipment creation"""
        # Mock failed DHL shipment creation
        mock_create.return_value = {
            'success': False,
            'error': 'Invalid address'
        }
        
        # Create integration
        integration = self.ShippingIntegration.objects.create(
            order=self.order,
            provider='dhl',
            status='pending'
        )
        
        # Call the service method
        from store.services.shipping_service import ShippingService
        result = ShippingService.create_dhl_shipment(integration.id)
        
        # Verify the result
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Invalid address')
        
        # Verify integration status wasn't changed to shipped
        integration.refresh_from_db()
        self.assertEqual(integration.status, 'pending')

class ShippingViewsTestCase(TestCase):
    """Test cases for shipping integration views"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.manager_user = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='testpass123',
            is_staff=True
        )
        
        self.seller_user = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='testpass123'
        )
        
        # Create test buyer
        self.buyer = User.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='testpass123'
        )
        
        # Create test product
        Product = apps.get_model('store', 'Product')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=Decimal('29.99'),
            stock_quantity=5,
            category='Electronics',
            seller=self.seller_user
        )
        
        # Create test order
        Order = apps.get_model('store', 'Order')
        self.order = Order.objects.create(
            user=self.buyer,
            total_amount=Decimal('29.99'),
            shipping_address='123 Test St, Test City',
            phone_number='123-456-7890',
            status='processing'
        )
        
        # Create order item
        OrderItem = apps.get_model('store', 'OrderItem')
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=Decimal('29.99')
        )
        
        # Get ShippingIntegration model
        self.ShippingIntegration = apps.get_model('store', 'ShippingIntegration')
    
    def test_shipping_integration_view_requires_login(self):
        """Test that shipping integration view requires login"""
        response = self.client.get(reverse('shipping_integration'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_shipping_integration_view_manager_access(self):
        """Test that managers can access shipping integration view"""
        # Login as manager
        self.client.login(username='manager', password='testpass123')
        
        response = self.client.get(reverse('shipping_integration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/shipping_integration.html')
    
    def test_shipping_integration_view_seller_access(self):
        """Test that sellers can access shipping integration view"""
        # Login as seller
        self.client.login(username='seller', password='testpass123')
        
        response = self.client.get(reverse('shipping_integration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/shipping_integration.html')
    
    def test_create_shipping_integration(self):
        """Test creating a shipping integration via view"""
        # Login as seller
        self.client.login(username='seller', password='testpass123')
        
        # Post data to create integration
        response = self.client.post(reverse('shipping_integration'), {
            'order': self.order.id,
            'provider': 'fedex',
            'shipping_cost': '15.99',
            'status': 'pending'
        })
        
        # Check that integration was created
        integrations = self.ShippingIntegration.objects.all()
        self.assertEqual(integrations.count(), 1)
        
        integration = integrations.first()
        self.assertEqual(integration.order, self.order)
        self.assertEqual(integration.provider, 'fedex')
        self.assertEqual(integration.shipping_cost, Decimal('15.99'))
        self.assertEqual(integration.status, 'pending')
    
    @patch('store.services.shipping_service.ShippingService.create_fedex_shipment')
    def test_process_shipping_integration(self, mock_create):
        """Test processing a shipping integration via view"""
        # Mock successful FedEx shipment creation
        mock_create.return_value = {
            'success': True,
            'tracking_number': 'FEDEX_TEST_12345',
            'label_url': 'https://fedex.com/label/12345',
            'cost': Decimal('12.50')
        }
        
        # Login as seller
        self.client.login(username='seller', password='testpass123')
        
        # Create integration
        integration = self.ShippingIntegration.objects.create(
            order=self.order,
            provider='fedex',
            status='pending'
        )
        
        # Post to process integration
        response = self.client.post(reverse('process_shipping_integration', args=[integration.id]))
        
        # Check that integration was updated
        integration.refresh_from_db()
        self.assertEqual(integration.status, 'shipped')
        self.assertEqual(integration.tracking_number, 'FEDEX_TEST_12345')
    
    def test_delete_shipping_integration(self):
        """Test deleting a shipping integration"""
        # Login as seller
        self.client.login(username='seller', password='testpass123')
        
        # Create integration
        integration = self.ShippingIntegration.objects.create(
            order=self.order,
            provider='fedex',
            status='pending'
        )
        
        # Delete integration
        response = self.client.post(reverse('delete_shipping_integration', args=[integration.id]))
        
        # Check that integration was deleted
        integrations = self.ShippingIntegration.objects.all()
        self.assertEqual(integrations.count(), 0)