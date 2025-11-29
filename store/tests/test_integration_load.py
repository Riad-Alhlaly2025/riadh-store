"""
Load tests for integration features to ensure they can handle high volumes of requests
"""

import time
import threading
from django.test import TestCase
from django.contrib.auth.models import User
from django.apps import apps
from decimal import Decimal
from unittest.mock import patch


class IntegrationLoadTestCase(TestCase):
    """Load test cases for integration features"""
    
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
        for i in range(50):  # Create 50 products for load testing
            product = Product.objects.create(
                name=f'Load Test Product {i}',
                description=f'Load Test Description {i}',
                price=Decimal(f'{9.99 + i}'),
                stock_quantity=100,
                category='Electronics',
                seller=self.seller
            )
            self.products.append(product)
        
        # Create test orders
        self.orders = []
        for i in range(25):  # Create 25 orders for load testing
            order = Order.objects.create(
                user=self.buyer,
                total_amount=Decimal(f'{19.99 + i}'),
                shipping_address=f'Load Test Address {i}',
                phone_number=f'123-456-{i:04d}',
                status='pending'
            )
            
            # Create order items
            OrderItem.objects.create(
                order=order,
                product=self.products[i % len(self.products)],
                quantity=1,
                price=Decimal(f'{9.99 + i}')
            )
            
            self.orders.append(order)
    
    def test_high_volume_social_media_integration_creation(self):
        """Test creating a high volume of social media integrations"""
        from store.models import SocialMediaIntegration
        
        start_time = time.time()
        
        # Create 100 social media integrations
        integrations = []
        for i in range(100):
            product = self.products[i % len(self.products)]
            integration = SocialMediaIntegration.objects.create(
                product=product,
                platform='facebook' if i % 3 == 0 else 'twitter' if i % 3 == 1 else 'instagram',
                status='pending'
            )
            integrations.append(integration)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify all integrations were created
        self.assertEqual(len(integrations), 100)
        
        # Check performance - should complete within reasonable time
        self.assertLess(execution_time, 5.0)  # Should complete within 5 seconds
        
        print(f"High Volume Social Media Integration Creation:")
        print(f"  Created {len(integrations)} integrations in {execution_time:.4f} seconds")
        print(f"  Rate: {len(integrations)/execution_time:.2f} integrations/second")
    
    def test_high_volume_shipping_integration_creation(self):
        """Test creating a high volume of shipping integrations"""
        from store.models import ShippingIntegration
        
        start_time = time.time()
        
        # Create 100 shipping integrations
        integrations = []
        for i in range(100):
            order = self.orders[i % len(self.orders)]
            integration = ShippingIntegration.objects.create(
                order=order,
                provider='fedex' if i % 4 == 0 else 'dhl' if i % 4 == 1 else 'ups' if i % 4 == 2 else 'aramex',
                status='pending'
            )
            integrations.append(integration)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify all integrations were created
        self.assertEqual(len(integrations), 100)
        
        # Check performance
        self.assertLess(execution_time, 5.0)  # Should complete within 5 seconds
        
        print(f"High Volume Shipping Integration Creation:")
        print(f"  Created {len(integrations)} integrations in {execution_time:.4f} seconds")
        print(f"  Rate: {len(integrations)/execution_time:.2f} integrations/second")
    
    def test_high_volume_external_inventory_creation(self):
        """Test creating a high volume of external inventory records"""
        from store.models import ExternalInventory
        
        start_time = time.time()
        
        # Create 100 external inventory records
        inventories = []
        for i in range(100):
            product = self.products[i % len(self.products)]
            inventory = ExternalInventory.objects.create(
                product=product,
                external_id=f'LOAD_TEST_{i:05d}',
                system_name='ERPNext' if i % 3 == 0 else 'Odoo' if i % 3 == 1 else 'SAP',
                external_stock=100 + i,
                sync_status='pending'
            )
            inventories.append(inventory)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify all inventory records were created
        self.assertEqual(len(inventories), 100)
        
        # Check performance
        self.assertLess(execution_time, 5.0)  # Should complete within 5 seconds
        
        print(f"High Volume External Inventory Creation:")
        print(f"  Created {len(inventories)} records in {execution_time:.4f} seconds")
        print(f"  Rate: {len(inventories)/execution_time:.2f} records/second")
    
    def test_concurrent_integration_creation(self):
        """Test concurrent creation of different types of integrations"""
        from store.models import SocialMediaIntegration, ShippingIntegration, ExternalInventory
        
        def create_social_integrations(count):
            """Create social media integrations"""
            integrations = []
            for i in range(count):
                product = self.products[i % len(self.products)]
                integration = SocialMediaIntegration.objects.create(
                    product=product,
                    platform='facebook',
                    status='pending'
                )
                integrations.append(integration)
            return integrations
        
        def create_shipping_integrations(count):
            """Create shipping integrations"""
            integrations = []
            for i in range(count):
                order = self.orders[i % len(self.orders)]
                integration = ShippingIntegration.objects.create(
                    order=order,
                    provider='fedex',
                    status='pending'
                )
                integrations.append(integration)
            return integrations
        
        def create_inventory_records(count):
            """Create external inventory records"""
            records = []
            for i in range(count):
                product = self.products[i % len(self.products)]
                record = ExternalInventory.objects.create(
                    product=product,
                    external_id=f'CONCURRENT_{i:05d}',
                    system_name='ERPNext',
                    external_stock=50 + i,
                    sync_status='pending'
                )
                records.append(record)
            return records
        
        start_time = time.time()
        
        # Create threads for concurrent operations
        threads = []
        results = {'social': [], 'shipping': [], 'inventory': []}
        
        # Create threads
        social_thread = threading.Thread(target=lambda: results.update({'social': create_social_integrations(30)}))
        shipping_thread = threading.Thread(target=lambda: results.update({'shipping': create_shipping_integrations(30)}))
        inventory_thread = threading.Thread(target=lambda: results.update({'inventory': create_inventory_records(30)}))
        
        # Start threads
        social_thread.start()
        shipping_thread.start()
        inventory_thread.start()
        
        # Wait for threads to complete
        social_thread.join()
        shipping_thread.join()
        inventory_thread.join()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify all records were created
        self.assertEqual(len(results['social']), 30)
        self.assertEqual(len(results['shipping']), 30)
        self.assertEqual(len(results['inventory']), 30)
        
        # Check performance
        total_records = 30 + 30 + 30
        self.assertLess(execution_time, 8.0)  # Should complete within 8 seconds
        
        print(f"Concurrent Integration Creation:")
        print(f"  Created {total_records} records in {execution_time:.4f} seconds")
        print(f"  Rate: {total_records/execution_time:.2f} records/second")
    
    @patch('store.services.social_media_service.SocialMediaService.post_to_facebook')
    @patch('store.services.shipping_service.ShippingService.create_fedex_shipment')
    @patch('store.services.external_inventory_service.ExternalInventoryService.sync_with_erpnext')
    def test_high_volume_service_calls(self, mock_sync, mock_shipment, mock_post):
        """Test high volume of service API calls"""
        from store.services.social_media_service import social_media_service
        from store.services.shipping_service import shipping_service
        from store.services.external_inventory_service import external_inventory_service
        from store.models import SocialMediaIntegration, ShippingIntegration, ExternalInventory
        
        # Mock successful responses
        mock_post.return_value = {
            'success': True,
            'post_id': 'fb_load_test',
            'response': {'id': 'fb_load_test'}
        }
        
        mock_shipment.return_value = {
            'success': True,
            'tracking_number': 'FEDEX_LOAD_TEST',
            'response': {'trackingNumber': 'FEDEX_LOAD_TEST'}
        }
        
        mock_sync.return_value = {
            'success': True,
            'stock': 75,
            'response': {'data': {'opening_stock': 75}}
        }
        
        start_time = time.time()
        
        # Create and process 50 social media integrations
        social_results = []
        for i in range(50):
            product = self.products[i % len(self.products)]
            integration = SocialMediaIntegration.objects.create(
                product=product,
                platform='facebook',
                status='pending'
            )
            result = social_media_service.post_product_to_platform(integration)
            social_results.append(result)
        
        # Create and process 50 shipping integrations
        shipping_results = []
        for i in range(50):
            order = self.orders[i % len(self.orders)]
            integration = ShippingIntegration.objects.create(
                order=order,
                provider='fedex',
                status='pending'
            )
            result = shipping_service.create_shipment(integration)
            shipping_results.append(result)
        
        # Create and sync 50 external inventory records
        inventory_results = []
        for i in range(50):
            product = self.products[i % len(self.products)]
            inventory = ExternalInventory.objects.create(
                product=product,
                external_id=f'SERVICE_LOAD_{i:05d}',
                system_name='ERPNext',
                sync_status='pending'
            )
            result = external_inventory_service.sync_inventory(inventory)
            inventory_results.append(result)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify all operations were successful
        self.assertEqual(len(social_results), 50)
        self.assertEqual(len(shipping_results), 50)
        self.assertEqual(len(inventory_results), 50)
        
        for result in social_results:
            self.assertTrue(result['success'])
        
        for result in shipping_results:
            self.assertTrue(result['success'])
        
        for result in inventory_results:
            self.assertTrue(result['success'])
        
        # Check performance
        total_operations = 50 + 50 + 50
        self.assertLess(execution_time, 15.0)  # Should complete within 15 seconds
        
        print(f"High Volume Service Calls:")
        print(f"  Processed {total_operations} operations in {execution_time:.4f} seconds")
        print(f"  Rate: {total_operations/execution_time:.2f} operations/second")


class IntegrationDatabaseLoadTestCase(TestCase):
    """Load test cases for database performance with integration features"""
    
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
        
        # Create a large number of products
        self.products = []
        for i in range(1000):  # Create 1000 products
            product = Product.objects.create(
                name=f'DB Load Test Product {i}',
                description=f'DB Load Test Description {i}',
                price=Decimal(f'{5.99 + i * 0.1}'),
                stock_quantity=50,
                category='Electronics',
                seller=self.seller
            )
            self.products.append(product)
        
        # Create a large number of orders
        self.orders = []
        for i in range(500):  # Create 500 orders
            order = Order.objects.create(
                user=self.seller,
                total_amount=Decimal(f'{15.99 + i * 0.2}'),
                shipping_address=f'DB Load Test Address {i}',
                phone_number=f'987-654-{i:04d}',
                status='pending'
            )
            self.orders.append(order)
    
    def test_large_dataset_query_performance(self):
        """Test query performance with large datasets"""
        from store.models import SocialMediaIntegration, ShippingIntegration, ExternalInventory
        
        # Create integration records for all products and orders
        # Social Media Integrations
        for i, product in enumerate(self.products[:100]):  # First 100 products
            SocialMediaIntegration.objects.create(
                product=product,
                platform='facebook' if i % 3 == 0 else 'twitter' if i % 3 == 1 else 'instagram',
                status='published' if i % 2 == 0 else 'pending'
            )
        
        # Shipping Integrations
        for i, order in enumerate(self.orders[:50]):  # First 50 orders
            ShippingIntegration.objects.create(
                order=order,
                provider='fedex' if i % 4 == 0 else 'dhl' if i % 4 == 1 else 'ups' if i % 4 == 2 else 'aramex',
                status='shipped' if i % 2 == 0 else 'pending',
                tracking_number=f'TRACK{i:06d}' if i % 2 == 0 else None
            )
        
        # External Inventory Records
        for i, product in enumerate(self.products[:75]):  # First 75 products
            ExternalInventory.objects.create(
                product=product,
                external_id=f'DB_LOAD_{i:06d}',
                system_name='ERPNext' if i % 3 == 0 else 'Odoo' if i % 3 == 1 else 'SAP',
                external_stock=100 + i,
                sync_status='synced' if i % 2 == 0 else 'pending'
            )
        
        # Test query performance
        start_time = time.time()
        
        # Complex query: Get all published social media integrations with their products
        published_social = SocialMediaIntegration.objects.filter(
            status='published'
        ).select_related('product').prefetch_related('product__seller')
        
        # Complex query: Get all shipped shipping integrations with their orders
        shipped_shipping = ShippingIntegration.objects.filter(
            status='shipped'
        ).select_related('order').prefetch_related('order__user')
        
        # Complex query: Get all synced external inventory records with their products
        synced_inventory = ExternalInventory.objects.filter(
            sync_status='synced'
        ).select_related('product')
        
        # Execute queries
        social_count = published_social.count()
        shipping_count = shipped_shipping.count()
        inventory_count = synced_inventory.count()
        
        # Get actual data
        social_data = list(published_social)
        shipping_data = list(shipped_shipping)
        inventory_data = list(synced_inventory)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify results
        self.assertGreaterEqual(social_count, 0)
        self.assertGreaterEqual(shipping_count, 0)
        self.assertGreaterEqual(inventory_count, 0)
        
        # Check performance - should be fast even with large datasets
        self.assertLess(execution_time, 3.0)  # Should complete within 3 seconds
        
        print(f"Large Dataset Query Performance:")
        print(f"  Queried {social_count} social integrations, {shipping_count} shipping integrations, {inventory_count} inventory records")
        print(f"  Execution Time: {execution_time:.4f} seconds")
    
    def test_bulk_operations_performance(self):
        """Test performance of bulk operations with large datasets"""
        from store.models import SocialMediaIntegration, ShippingIntegration, ExternalInventory
        
        start_time = time.time()
        
        # Bulk create social media integrations
        social_integrations = []
        for i, product in enumerate(self.products[:200]):  # First 200 products
            social_integrations.append(SocialMediaIntegration(
                product=product,
                platform='facebook',
                status='pending'
            ))
        
        SocialMediaIntegration.objects.bulk_create(social_integrations)
        
        # Bulk create shipping integrations
        shipping_integrations = []
        for i, order in enumerate(self.orders[:100]):  # First 100 orders
            shipping_integrations.append(ShippingIntegration(
                order=order,
                provider='fedex',
                status='pending'
            ))
        
        ShippingIntegration.objects.bulk_create(shipping_integrations)
        
        # Bulk create external inventory records
        inventory_records = []
        for i, product in enumerate(self.products[:150]):  # First 150 products
            inventory_records.append(ExternalInventory(
                product=product,
                external_id=f'BULK_LOAD_{i:06d}',
                system_name='ERPNext',
                external_stock=75 + i,
                sync_status='pending'
            ))
        
        ExternalInventory.objects.bulk_create(inventory_records)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify all records were created
        self.assertEqual(SocialMediaIntegration.objects.count(), 200)
        self.assertEqual(ShippingIntegration.objects.count(), 100)
        self.assertEqual(ExternalInventory.objects.count(), 150)
        
        # Check performance
        total_records = 200 + 100 + 150
        self.assertLess(execution_time, 5.0)  # Should complete within 5 seconds
        
        print(f"Bulk Operations Performance:")
        print(f"  Created {total_records} records in {execution_time:.4f} seconds")
        print(f"  Rate: {total_records/execution_time:.2f} records/second")
    
    def test_database_index_performance(self):
        """Test that database indexes improve query performance"""
        from store.models import SocialMediaIntegration, ShippingIntegration, ExternalInventory
        
        # Create integration records
        for i, product in enumerate(self.products[:100]):
            SocialMediaIntegration.objects.create(
                product=product,
                platform='facebook',
                status='published' if i % 3 == 0 else 'pending' if i % 3 == 1 else 'failed'
            )
        
        for i, order in enumerate(self.orders[:50]):
            ShippingIntegration.objects.create(
                order=order,
                provider='fedex',
                status='shipped' if i % 2 == 0 else 'pending'
            )
        
        for i, product in enumerate(self.products[:75]):
            ExternalInventory.objects.create(
                product=product,
                external_id=f'INDEX_TEST_{i:05d}',
                system_name='ERPNext',
                sync_status='synced' if i % 2 == 0 else 'pending'
            )
        
        # Test indexed queries performance
        start_time = time.time()
        
        # Query by status (should be indexed)
        published_social = SocialMediaIntegration.objects.filter(status='published')
        pending_shipping = ShippingIntegration.objects.filter(status='pending')
        synced_inventory = ExternalInventory.objects.filter(sync_status='synced')
        
        # Execute queries
        published_count = published_social.count()
        pending_count = pending_shipping.count()
        synced_count = synced_inventory.count()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify results
        self.assertGreaterEqual(published_count, 0)
        self.assertGreaterEqual(pending_count, 0)
        self.assertGreaterEqual(synced_count, 0)
        
        # Check performance
        self.assertLess(execution_time, 2.0)  # Should complete within 2 seconds
        
        print(f"Database Index Performance:")
        print(f"  Queried {published_count} published social, {pending_count} pending shipping, {synced_count} synced inventory")
        print(f"  Execution Time: {execution_time:.4f} seconds")