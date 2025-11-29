"""
Unit tests for external inventory integration functionality
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.apps import apps
from django.urls import reverse
from decimal import Decimal
from unittest.mock import patch, MagicMock
import json

class ExternalInventoryTestCase(TestCase):
    """Test cases for ExternalInventory model and service"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user (seller)
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
        
        # Get ExternalInventory model
        self.ExternalInventory = apps.get_model('store', 'ExternalInventory')
    
    def test_external_inventory_creation(self):
        """Test creating an external inventory record"""
        # Create external inventory
        inventory = self.ExternalInventory.objects.create(
            product=self.product,
            system_name='ERPNext',
            external_id='ERP12345',
            external_stock=100,
            sync_status='synced'
        )
        
        # Verify inventory was created
        self.assertIsNotNone(inventory.id)
        self.assertEqual(inventory.product, self.product)
        self.assertEqual(inventory.system_name, 'ERPNext')
        self.assertEqual(inventory.external_id, 'ERP12345')
        self.assertEqual(inventory.external_stock, 100)
        self.assertEqual(inventory.sync_status, 'synced')
    
    def test_external_inventory_str_representation(self):
        """Test string representation of external inventory"""
        inventory = self.ExternalInventory.objects.create(
            product=self.product,
            system_name='Odoo',
            external_id='ODOO67890',
            sync_status='pending'
        )
        
        expected_str = f"{self.product.name} in Odoo (ODOO67890)"
        self.assertEqual(str(inventory), expected_str)
    
    def test_get_out_of_sync_inventory(self):
        """Test getting out-of-sync inventory records"""
        # Create synced inventory
        self.ExternalInventory.objects.create(
            product=self.product,
            system_name='ERPNext',
            external_id='ERP12345',
            external_stock=100,
            sync_status='synced'
        )
        
        # Create another product
        Product = apps.get_model('store', 'Product')
        product2 = Product.objects.create(
            name='Test Product 2',
            description='Test Description 2',
            price=Decimal('39.99'),
            stock_quantity=3,
            category='Electronics',
            seller=self.seller
        )
        
        # Create pending sync inventory
        self.ExternalInventory.objects.create(
            product=product2,
            system_name='Odoo',
            external_id='ODOO67890',
            external_stock=50,
            sync_status='pending'
        )
        
        # Test filtering by sync status
        pending_sync = self.ExternalInventory.objects.filter(sync_status='pending')
        self.assertEqual(pending_sync.count(), 1)
        self.assertEqual(pending_sync.first().system_name, 'Odoo')
    
    def test_inventory_stock_mismatch_detection(self):
        """Test detection of stock mismatches"""
        # Create external inventory with mismatched stock
        inventory = self.ExternalInventory.objects.create(
            product=self.product,
            system_name='SAP',
            external_id='SAP54321',
            external_stock=50,  # External system shows 50
            sync_status='synced'
        )
        
        # Local product stock is 5 (from setUp)
        self.assertNotEqual(self.product.stock_quantity, inventory.external_stock)
        
        # Calculate difference
        difference = inventory.external_stock - self.product.stock_quantity
        self.assertEqual(difference, 45)  # 50 - 5 = 45
    
    @patch('store.services.external_inventory_service.ExternalInventoryService.sync_with_erpnext')
    def test_erpnext_sync_success(self, mock_sync):
        """Test successful ERPNext synchronization"""
        # Mock successful ERPNext sync
        mock_sync.return_value = {
            'success': True,
            'external_stock': 75,
            'last_synced': '2023-01-01T12:00:00Z'
        }
        
        # Create inventory record
        inventory = self.ExternalInventory.objects.create(
            product=self.product,
            system_name='ERPNext',
            external_id='ERP12345',
            external_stock=100,
            sync_status='pending'
        )
        
        # Call the service method
        from store.services.external_inventory_service import ExternalInventoryService
        result = ExternalInventoryService.sync_with_erpnext(inventory.id)
        
        # Verify the result
        self.assertTrue(result['success'])
        self.assertEqual(result['external_stock'], 75)
        
        # Verify inventory was updated
        inventory.refresh_from_db()
        self.assertEqual(inventory.sync_status, 'synced')
        self.assertEqual(inventory.external_stock, 75)
    
    @patch('store.services.external_inventory_service.ExternalInventoryService.sync_with_odoo')
    def test_odoo_sync_failure(self, mock_sync):
        """Test failed Odoo synchronization"""
        # Mock failed Odoo sync
        mock_sync.return_value = {
            'success': False,
            'error': 'Connection timeout'
        }
        
        # Create inventory record
        inventory = self.ExternalInventory.objects.create(
            product=self.product,
            system_name='Odoo',
            external_id='ODOO67890',
            external_stock=50,
            sync_status='pending'
        )
        
        # Call the service method
        from store.services.external_inventory_service import ExternalInventoryService
        result = ExternalInventoryService.sync_with_odoo(inventory.id)
        
        # Verify the result
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Connection timeout')
        
        # Verify inventory status wasn't changed to synced
        inventory.refresh_from_db()
        self.assertEqual(inventory.sync_status, 'pending')

class ExternalInventoryViewsTestCase(TestCase):
    """Test cases for external inventory integration views"""
    
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
        
        # Get ExternalInventory model
        self.ExternalInventory = apps.get_model('store', 'ExternalInventory')
    
    def test_external_inventory_view_requires_login(self):
        """Test that external inventory view requires login"""
        response = self.client.get(reverse('external_inventory'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_external_inventory_view_manager_access(self):
        """Test that managers can access external inventory view"""
        # Login as manager
        self.client.login(username='manager', password='testpass123')
        
        response = self.client.get(reverse('external_inventory'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/external_inventory.html')
    
    def test_external_inventory_view_seller_access(self):
        """Test that sellers can access external inventory view"""
        # Login as seller
        self.client.login(username='seller', password='testpass123')
        
        response = self.client.get(reverse('external_inventory'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/external_inventory.html')
    
    def test_create_external_inventory(self):
        """Test creating an external inventory record via view"""
        # Login as seller
        self.client.login(username='seller', password='testpass123')
        
        # Post data to create inventory record
        response = self.client.post(reverse('external_inventory'), {
            'product': self.product.id,
            'system_name': 'ERPNext',
            'external_id': 'ERP12345',
            'external_stock': 100,
            'sync_status': 'pending'
        })
        
        # Check that inventory record was created
        inventories = self.ExternalInventory.objects.all()
        self.assertEqual(inventories.count(), 1)
        
        inventory = inventories.first()
        self.assertEqual(inventory.product, self.product)
        self.assertEqual(inventory.system_name, 'ERPNext')
        self.assertEqual(inventory.external_id, 'ERP12345')
        self.assertEqual(inventory.external_stock, 100)
        self.assertEqual(inventory.sync_status, 'pending')
    
    @patch('store.services.external_inventory_service.ExternalInventoryService.sync_with_erpnext')
    def test_sync_external_inventory(self, mock_sync):
        """Test syncing an external inventory record via view"""
        # Mock successful ERPNext sync
        mock_sync.return_value = {
            'success': True,
            'external_stock': 75,
            'last_synced': '2023-01-01T12:00:00Z'
        }
        
        # Login as seller
        self.client.login(username='seller', password='testpass123')
        
        # Create inventory record
        inventory = self.ExternalInventory.objects.create(
            product=self.product,
            system_name='ERPNext',
            external_id='ERP12345',
            external_stock=100,
            sync_status='pending'
        )
        
        # Post to sync inventory
        response = self.client.post(reverse('sync_external_inventory', args=[inventory.id]))
        
        # Check that inventory was updated
        inventory.refresh_from_db()
        self.assertEqual(inventory.sync_status, 'synced')
        self.assertEqual(inventory.external_stock, 75)
    
    def test_delete_external_inventory(self):
        """Test deleting an external inventory record"""
        # Login as seller
        self.client.login(username='seller', password='testpass123')
        
        # Create inventory record
        inventory = self.ExternalInventory.objects.create(
            product=self.product,
            system_name='ERPNext',
            external_id='ERP12345',
            external_stock=100,
            sync_status='pending'
        )
        
        # Delete inventory record
        response = self.client.post(reverse('delete_external_inventory', args=[inventory.id]))
        
        # Check that inventory record was deleted
        inventories = self.ExternalInventory.objects.all()
        self.assertEqual(inventories.count(), 0)