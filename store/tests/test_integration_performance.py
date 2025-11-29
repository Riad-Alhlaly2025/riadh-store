"""
Performance tests for integration features
"""

import time
import psutil
import os
from django.test import TestCase
from django.contrib.auth.models import User
from django.apps import apps
from decimal import Decimal
from unittest.mock import patch


class IntegrationPerformanceTestCase(TestCase):
    """Test cases for performance of integration features"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.seller = User.objects.create_user(
            username='testseller',
            email='seller@example.com',
            password='testpass123'
        )
        
        self.buyer = User.objects.create_user(
            username='testbuyer',
            email='buyer@example.com',
            password='testpass123'
        )
        
        # Get models
        Product = apps.get_model('store', 'Product')
        Order = apps.get_model('store', 'Order')
        OrderItem = apps.get_model('store', 'OrderItem')
        
        # Create test products
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
        
        # Create test orders
        self.orders = []
        for i in range(5):
            order = Order.objects.create(
                user=self.buyer,
                total_amount=Decimal(f'{20 + i}.99'),
                shipping_address=f'Test Address {i}',
                phone_number=f'123-456-789{i}',
                status='pending'
            )
            
            # Create order items
            OrderItem.objects.create(
                order=order,
                product=self.products[i],
                quantity=1,
                price=Decimal(f'{10 + i}.99')
            )
            
            self.orders.append(order)
    
    def measure_performance(self, func, *args, **kwargs):
        """Measure execution time and memory usage of a function"""
        # Get initial process info
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Measure execution time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        execution_time = end_time - start_time
        memory_used = final_memory - initial_memory
        
        return {
            'result': result,
            'execution_time': execution_time,
            'memory_used': memory_used
        }
    
    def test_social_media_integration_performance(self):
        """Test performance of social media integration creation"""
        from store.models import SocialMediaIntegration
        
        # Create multiple social media integrations
        def create_integrations():
            integrations = []
            for product in self.products[:5]:  # Use first 5 products
                integration = SocialMediaIntegration.objects.create(
                    product=product,
                    platform='facebook',
                    status='pending'
                )
                integrations.append(integration)
            return integrations
        
        # Measure performance
        perf_data = self.measure_performance(create_integrations)
        
        # Verify all integrations were created
        self.assertEqual(len(perf_data['result']), 5)
        
        # Check performance metrics (these are just examples, adjust based on requirements)
        self.assertLess(perf_data['execution_time'], 2.0)  # Should complete within 2 seconds
        self.assertLess(perf_data['memory_used'], 10.0)    # Should use less than 10MB additional memory
        
        print(f"Social Media Integration Performance:")
        print(f"  Execution Time: {perf_data['execution_time']:.4f} seconds")
        print(f"  Memory Used: {perf_data['memory_used']:.2f} MB")
    
    def test_shipping_integration_performance(self):
        """Test performance of shipping integration creation"""
        from store.models import ShippingIntegration
        
        # Create multiple shipping integrations
        def create_integrations():
            integrations = []
            for order in self.orders:
                integration = ShippingIntegration.objects.create(
                    order=order,
                    provider='fedex',
                    status='pending'
                )
                integrations.append(integration)
            return integrations
        
        # Measure performance
        perf_data = self.measure_performance(create_integrations)
        
        # Verify all integrations were created
        self.assertEqual(len(perf_data['result']), 5)
        
        # Check performance metrics
        self.assertLess(perf_data['execution_time'], 2.0)  # Should complete within 2 seconds
        self.assertLess(perf_data['memory_used'], 10.0)    # Should use less than 10MB additional memory
        
        print(f"Shipping Integration Performance:")
        print(f"  Execution Time: {perf_data['execution_time']:.4f} seconds")
        print(f"  Memory Used: {perf_data['memory_used']:.2f} MB")
    
    def test_external_inventory_performance(self):
        """Test performance of external inventory creation"""
        from store.models import ExternalInventory
        
        # Create multiple inventory records
        def create_inventories():
            inventories = []
            for product in self.products:
                inventory = ExternalInventory.objects.create(
                    product=product,
                    external_id=f'EXT{product.id:05d}',
                    system_name='ERPNext',
                    sync_status='pending'
                )
                inventories.append(inventory)
            return inventories
        
        # Measure performance
        perf_data = self.measure_performance(create_inventories)
        
        # Verify all inventory records were created
        self.assertEqual(len(perf_data['result']), 10)
        
        # Check performance metrics
        self.assertLess(perf_data['execution_time'], 3.0)  # Should complete within 3 seconds
        self.assertLess(perf_data['memory_used'], 15.0)    # Should use less than 15MB additional memory
        
        print(f"External Inventory Performance:")
        print(f"  Execution Time: {perf_data['execution_time']:.4f} seconds")
        print(f"  Memory Used: {perf_data['memory_used']:.2f} MB")
    
    def test_analytics_data_retrieval_performance(self):
        """Test performance of analytics data retrieval"""
        from store.services.analytics_service import analytics_service
        
        # Create some analytics events
        AnalyticsIntegration = apps.get_model('store', 'AnalyticsIntegration')
        for i in range(50):
            AnalyticsIntegration.objects.create(
                user=self.buyer,
                event_type='page_view',
                url=f'https://test-store.com/product/{i}/',
                timestamp=time.time()
            )
        
        # Test basic analytics retrieval
        def get_basic_analytics():
            return analytics_service.get_basic_analytics()
        
        perf_data = self.measure_performance(get_basic_analytics)
        
        # Verify success
        self.assertTrue(perf_data['result']['success'])
        
        # Check performance metrics
        self.assertLess(perf_data['execution_time'], 1.0)  # Should complete within 1 second
        self.assertLess(perf_data['memory_used'], 5.0)     # Should use less than 5MB additional memory
        
        print(f"Analytics Data Retrieval Performance:")
        print(f"  Execution Time: {perf_data['execution_time']:.4f} seconds")
        print(f"  Memory Used: {perf_data['memory_used']:.2f} MB")
    
    def test_bulk_operations_performance(self):
        """Test performance of bulk operations"""
        from store.models import SocialMediaIntegration, ShippingIntegration, ExternalInventory
        
        # Test bulk creation
        def bulk_create_integrations():
            # Create social media integrations
            social_integrations = []
            for product in self.products[:5]:
                social_integrations.append(SocialMediaIntegration(
                    product=product,
                    platform='facebook',
                    status='pending'
                ))
            
            SocialMediaIntegration.objects.bulk_create(social_integrations)
            
            # Create shipping integrations
            shipping_integrations = []
            for order in self.orders:
                shipping_integrations.append(ShippingIntegration(
                    order=order,
                    provider='fedex',
                    status='pending'
                ))
            
            ShippingIntegration.objects.bulk_create(shipping_integrations)
            
            # Create external inventory records
            inventory_records = []
            for product in self.products:
                inventory_records.append(ExternalInventory(
                    product=product,
                    external_id=f'BULK{product.id:05d}',
                    system_name='Odoo',
                    sync_status='pending'
                ))
            
            ExternalInventory.objects.bulk_create(inventory_records)
            
            return len(social_integrations) + len(shipping_integrations) + len(inventory_records)
        
        # Measure performance
        perf_data = self.measure_performance(bulk_create_integrations)
        
        # Verify all records were created
        self.assertEqual(perf_data['result'], 20)  # 5 + 5 + 10
        
        # Check performance metrics
        self.assertLess(perf_data['execution_time'], 1.5)  # Should complete within 1.5 seconds
        self.assertLess(perf_data['memory_used'], 8.0)     # Should use less than 8MB additional memory
        
        print(f"Bulk Operations Performance:")
        print(f"  Execution Time: {perf_data['execution_time']:.4f} seconds")
        print(f"  Memory Used: {perf_data['memory_used']:.2f} MB")


class IntegrationAPIServicePerformanceTestCase(TestCase):
    """Test cases for performance of integration API services"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.seller = User.objects.create_user(
            username='testseller',
            email='seller@example.com',
            password='testpass123'
        )
        
        # Get models
        Product = apps.get_model('store', 'Product')
        Order = apps.get_model('store', 'Order')
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=Decimal('29.99'),
            stock_quantity=5,
            category='Electronics',
            seller=self.seller
        )
        
        # Create test order
        self.order = Order.objects.create(
            user=self.seller,
            total_amount=Decimal('29.99'),
            shipping_address='Test Address',
            phone_number='123-456-7890',
            status='pending'
        )
    
    @patch('store.services.social_media_service.SocialMediaService.post_to_facebook')
    def test_social_media_service_performance(self, mock_post):
        """Test performance of social media service"""
        from store.services.social_media_service import social_media_service
        from store.models import SocialMediaIntegration
        
        # Mock successful response
        mock_post.return_value = {
            'success': True,
            'post_id': 'fb_test_post_123',
            'response': {'id': 'fb_test_post_123'}
        }
        
        # Create integration
        integration = SocialMediaIntegration.objects.create(
            product=self.product,
            platform='facebook',
            status='pending'
        )
        
        # Measure service performance
        start_time = time.time()
        result = social_media_service.post_product_to_platform(integration)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Verify success
        self.assertTrue(result['success'])
        
        # Check performance (should be fast since we're mocking the API call)
        self.assertLess(execution_time, 0.5)  # Should complete within 0.5 seconds
        
        print(f"Social Media Service Performance:")
        print(f"  Execution Time: {execution_time:.4f} seconds")
    
    @patch('store.services.shipping_service.ShippingService.create_fedex_shipment')
    def test_shipping_service_performance(self, mock_create):
        """Test performance of shipping service"""
        from store.services.shipping_service import shipping_service
        from store.models import ShippingIntegration
        
        # Mock successful response
        mock_create.return_value = {
            'success': True,
            'tracking_number': 'FEDEX_TEST_12345',
            'response': {'trackingNumber': 'FEDEX_TEST_12345'}
        }
        
        # Create integration
        integration = ShippingIntegration.objects.create(
            order=self.order,
            provider='fedex',
            status='pending'
        )
        
        # Measure service performance
        start_time = time.time()
        result = shipping_service.create_shipment(integration)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Verify success
        self.assertTrue(result['success'])
        
        # Check performance
        self.assertLess(execution_time, 0.5)  # Should complete within 0.5 seconds
        
        print(f"Shipping Service Performance:")
        print(f"  Execution Time: {execution_time:.4f} seconds")
    
    @patch('store.services.external_inventory_service.ExternalInventoryService.sync_with_erpnext')
    def test_external_inventory_service_performance(self, mock_sync):
        """Test performance of external inventory service"""
        from store.services.external_inventory_service import external_inventory_service
        from store.models import ExternalInventory
        
        # Mock successful response
        mock_sync.return_value = {
            'success': True,
            'stock': 75,
            'response': {'data': {'opening_stock': 75}}
        }
        
        # Create inventory record
        inventory = ExternalInventory.objects.create(
            product=self.product,
            external_id='ERP12345',
            system_name='ERPNext',
            sync_status='pending'
        )
        
        # Measure service performance
        start_time = time.time()
        result = external_inventory_service.sync_inventory(inventory)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Verify success
        self.assertTrue(result['success'])
        
        # Check performance
        self.assertLess(execution_time, 0.5)  # Should complete within 0.5 seconds
        
        print(f"External Inventory Service Performance:")
        print(f"  Execution Time: {execution_time:.4f} seconds")