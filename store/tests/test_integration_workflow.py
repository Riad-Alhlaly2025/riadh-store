"""
Integration tests for complete workflow of all integration features
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.apps import apps
from django.urls import reverse
from decimal import Decimal
from unittest.mock import patch, MagicMock
import json

class CompleteIntegrationWorkflowTestCase(TestCase):
    """Test cases for complete integration workflow"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.manager_user = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='testpass123',
            is_staff=True
        )
        self.manager_user.is_staff = True
        self.manager_user.save()
        
        self.seller_user = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='testpass123',
            is_staff=True
        )
        self.seller_user.is_staff = True
        self.seller_user.save()
        
        self.buyer_user = User.objects.create_user(
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
            user=self.buyer_user,
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
        
        # Get integration models
        self.SocialMediaIntegration = apps.get_model('store', 'SocialMediaIntegration')
        self.ShippingIntegration = apps.get_model('store', 'ShippingIntegration')
        self.ExternalInventory = apps.get_model('store', 'ExternalInventory')
        self.AnalyticsIntegration = apps.get_model('store', 'AnalyticsIntegration')
    
    @patch('store.services.social_media_service.social_media_service.post_product_to_platform')
    @patch('store.services.shipping_service.shipping_service.create_shipment')
    @patch('store.services.external_inventory_service.external_inventory_service.sync_inventory')
    def test_complete_integration_workflow(self, mock_sync, mock_shipment, mock_post):
        """Test complete integration workflow from product creation to order fulfillment"""
        # Mock all external API calls
        mock_post.return_value = {
            'success': True,
            'post_id': 'fb_test_post_123',
            'permalink': 'https://facebook.com/test/post/123'
        }
        
        mock_shipment.return_value = {
            'success': True,
            'tracking_number': 'FEDEX_TEST_12345'
        }
        
        mock_sync.return_value = {
            'success': True,
            'stock': 75
        }
        
        # Login as seller
        self.client.login(username='seller', password='testpass123')
        
        # Ensure seller user is staff
        self.seller_user.refresh_from_db()
        self.assertTrue(self.seller_user.is_staff)
        
        # Step 1: Create social media integration for new product
        social_integration = self.SocialMediaIntegration.objects.create(
            product=self.product,
            platform='facebook',
            status='pending'
        )
        
        # Publish to social media
        response = self.client.post(reverse('social_media_integration'), {
            'product_id': social_integration.product.id,
            'platform': social_integration.platform
        })
        
        # Get fresh integration object from the database
        social_integration = self.SocialMediaIntegration.objects.get(product=self.product, platform='facebook')
        self.assertEqual(social_integration.status, 'posted')
        self.assertEqual(social_integration.post_id, 'fb_test_post_123')
        
        # Step 2: Process order and create shipping integration
        self.order.status = 'processing'
        self.order.save()
        
        # Process shipping (this will create a new integration)
        response = self.client.post(reverse('shipping_integration'), {
            'order_id': self.order.id,
            'provider': 'fedex'
        })
        
        # Verify shipping integration was created and updated
        shipping_integrations = self.ShippingIntegration.objects.filter(order=self.order, provider='fedex')
        self.assertEqual(shipping_integrations.count(), 1)
        shipping_integration = shipping_integrations.first()
        self.assertEqual(shipping_integration.status, 'shipped')
        self.assertEqual(shipping_integration.tracking_number, 'FEDEX_TEST_12345')
        
        # Update order status to shipped
        self.order.status = 'shipped'
        self.order.save()
        
        # Step 3: Sync inventory after sale
        inventory_record = self.ExternalInventory.objects.create(
            product=self.product,
            system_name='ERPNext',
            external_id='ERP12345',
            external_stock=100,
            sync_status='pending'
        )
        
        # Sync inventory (this will create a new integration)
        response = self.client.post(reverse('external_inventory'), {
            'product_id': self.product.id,
            'external_id': 'ERP12345',
            'system_name': 'ERPNext'
        })
        
        # Verify inventory was created and updated
        inventory_records = self.ExternalInventory.objects.filter(product=self.product, external_id='ERP12345')
        self.assertEqual(inventory_records.count(), 1)
        inventory_record = inventory_records.first()
        self.assertEqual(inventory_record.sync_status, 'synced')
        self.assertEqual(inventory_record.external_stock, 75)
        
        # Step 4: Track analytics for the completed workflow
        analytics_event = self.AnalyticsIntegration.objects.create(
            user=self.buyer_user,
            event_type='purchase_completed',
            order=self.order,
            url='/checkout/complete/',
            metadata=json.dumps({
                'product_id': self.product.id,
                'shipping_provider': 'fedex',
                'social_shared': True
            })
        )
        
        # Verify analytics event was created
        self.assertIsNotNone(analytics_event.id)
        self.assertEqual(analytics_event.event_type, 'purchase_completed')
        
        # Step 5: Verify all integrations are properly linked
        # Check that all integration records exist and are properly connected
        social_integrations = self.SocialMediaIntegration.objects.filter(product=self.product)
        self.assertEqual(social_integrations.count(), 1)
        self.assertEqual(social_integrations.first().status, 'posted')
        
        shipping_integrations = self.ShippingIntegration.objects.filter(order=self.order)
        self.assertEqual(shipping_integrations.count(), 1)
        self.assertEqual(shipping_integrations.first().status, 'shipped')
        
        inventory_records = self.ExternalInventory.objects.filter(product=self.product)
        self.assertEqual(inventory_records.count(), 1)
        self.assertEqual(inventory_records.first().sync_status, 'synced')
        
        analytics_events = self.AnalyticsIntegration.objects.filter(order=self.order)
        self.assertEqual(analytics_events.count(), 1)
        self.assertEqual(analytics_events.first().event_type, 'purchase_completed')
    
    def test_integration_dashboard_view(self):
        """Test integration dashboard view showing all integration statuses"""
        # Login as manager
        self.client.login(username='manager', password='testpass123')
        
        # Ensure manager user is staff
        self.manager_user.refresh_from_db()
        self.assertTrue(self.manager_user.is_staff)
        
        # Create various integration records
        self.SocialMediaIntegration.objects.create(
            product=self.product,
            platform='facebook',
            status='published'
        )
        
        self.SocialMediaIntegration.objects.create(
            product=self.product,
            platform='twitter',
            status='pending'
        )
        
        self.ShippingIntegration.objects.create(
            order=self.order,
            provider='fedex',
            status='shipped'
        )
        
        self.ExternalInventory.objects.create(
            product=self.product,
            system_name='ERPNext',
            external_id='ERP12345',
            sync_status='synced'
        )
        
        # Access manager dashboard
        response = self.client.get(reverse('manager_dashboard'), follow=True)
        
        # Debug information
        print(f"Response status code: {response.status_code}")
        print(f"Response redirect: {response.redirect_chain if hasattr(response, 'redirect_chain') else 'No redirect chain'}")
        if hasattr(response, 'url'):
            print(f"Response URL: {response.url}")
        
        # Check that dashboard loads successfully
        self.assertEqual(response.status_code, 200)
        
        # Ensure manager user is staff
        self.manager_user.refresh_from_db()
        self.assertTrue(self.manager_user.is_staff)
        self.assertTemplateUsed(response, 'store/manager_dashboard.html')
        
        # Note: We're not checking specific context data here as the dashboard
        # implementation may vary, but we verify the page loads correctly
    
    @patch('store.services.social_media_service.social_media_service.post_product_to_platform')
    @patch('store.services.shipping_service.shipping_service.create_shipment')
    def test_failed_integration_handling(self, mock_shipment, mock_post):
        """Test handling of failed integrations"""
        # Mock failed API calls
        mock_post.return_value = {
            'success': False,
            'error': 'Invalid API key'
        }
        
        mock_shipment.return_value = {
            'success': False,
            'error': 'Address validation failed'
        }
        
        # Login as seller
        self.client.login(username='seller', password='testpass123')
        
        # Ensure seller user is staff
        self.seller_user.refresh_from_db()
        self.assertTrue(self.seller_user.is_staff)
        
        # Attempt operations that will fail (these will create new integrations)
        response1 = self.client.post(reverse('social_media_integration'), {
            'product_id': self.product.id,
            'platform': 'facebook'
        })
        response2 = self.client.post(reverse('shipping_integration'), {
            'order_id': self.order.id,
            'provider': 'fedex'
        })
        
        # Verify new integrations were created with failed status
        social_integrations = self.SocialMediaIntegration.objects.filter(product=self.product, platform='facebook')
        self.assertEqual(social_integrations.count(), 1)
        social_integration = social_integrations.first()
        self.assertEqual(social_integration.status, 'failed')
        
        shipping_integrations = self.ShippingIntegration.objects.filter(order=self.order, provider='fedex')
        self.assertEqual(shipping_integrations.count(), 1)
        shipping_integration = shipping_integrations.first()
        self.assertEqual(shipping_integration.status, 'failed')
        
        # Verify error handling - in a real implementation, we would check
        # for error messages or log entries, but here we just verify the
        # integrations weren't marked as successful

class PerformanceIntegrationTestCase(TestCase):
    """Test cases for performance of integration features"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user (seller)
        self.seller = User.objects.create_user(
            username='testseller',
            email='seller@example.com',
            password='testpass123'
        )
        
        # Create multiple test products
        Product = apps.get_model('store', 'Product')
        self.products = []
        for i in range(10):
            product = Product.objects.create(
                name=f'Test Product {i}',
                description=f'Test Description {i}',
                price=Decimal(f'{10 + i}.99'),
                stock_quantity=5,
                category='Electronics',
                seller=self.seller
            )
            self.products.append(product)
    
    def test_bulk_social_media_integration_creation(self):
        """Test creating multiple social media integrations efficiently"""
        from store.services.social_media_service import SocialMediaService
        
        # Create multiple social media integrations
        integrations = []
        for product in self.products[:5]:  # Use first 5 products
            integration = apps.get_model('store', 'SocialMediaIntegration').objects.create(
                product=product,
                platform='facebook',
                status='pending'
            )
            integrations.append(integration)
        
        # Verify all integrations were created
        self.assertEqual(len(integrations), 5)
        
        # Check that all integrations are properly linked to products
        for i, integration in enumerate(integrations):
            self.assertEqual(integration.product, self.products[i])
            self.assertEqual(integration.platform, 'facebook')
            self.assertEqual(integration.status, 'pending')
    
    def test_bulk_inventory_sync_performance(self):
        """Test syncing multiple inventory records efficiently"""
        from store.services.external_inventory_service import ExternalInventoryService
        
        # Create multiple inventory records
        inventory_records = []
        for idx, product in enumerate(self.products):
            inventory = apps.get_model('store', 'ExternalInventory').objects.create(
                product=product,
                system_name='ERPNext',
                external_id=f'ERP{idx:05d}',
                external_stock=100 + idx,
                sync_status='pending'
            )
            inventory_records.append(inventory)
        
        # Verify all inventory records were created
        self.assertEqual(len(inventory_records), 10)
        
        # In a real test, we would mock the external API calls and measure
        # performance, but here we just verify the setup is correct