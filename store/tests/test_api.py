"""
Unit tests for API views
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.apps import apps
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

class ProductAPITestCase(TestCase):
    """Test cases for product API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test products
        Product = apps.get_model('store', 'Product')
        self.product1 = Product.objects.create(
            name='Test Product 1',
            description='Test Description 1',
            price=Decimal('19.99'),
            category='Test Category',
            stock_quantity=10
        )
        
        self.product2 = Product.objects.create(
            name='Test Product 2',
            description='Test Description 2',
            price=Decimal('29.99'),
            category='Test Category',
            stock_quantity=5
        )
    
    def test_product_list_api(self):
        """Test product list API endpoint"""
        url = reverse('store_api:product_list')
        response = self.client.get(url)
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_product_detail_api(self):
        """Test product detail API endpoint"""
        url = reverse('store_api:product_detail', kwargs={'pk': self.product1.pk})
        response = self.client.get(url)
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product 1')
    
    def test_category_list_api(self):
        """Test category list API endpoint"""
        url = reverse('store_api:category_list')
        response = self.client.get(url)
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # One category
        self.assertEqual(response.data[0]['category'], 'Test Category')

class OrderAPITestCase(TestCase):
    """Test cases for order API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test order
        Order = apps.get_model('store', 'Order')
        self.order = Order.objects.create(
            user=self.user,
            total_amount=Decimal('49.98'),
            status='pending'
        )
    
    def test_order_list_api_authenticated(self):
        """Test order list API endpoint with authentication"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('store_api:order_list')
        response = self.client.get(url)
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.order.id)
    
    def test_order_list_api_unauthenticated(self):
        """Test order list API endpoint without authentication"""
        url = reverse('store_api:order_list')
        response = self.client.get(url)
        
        # Verify response - should be empty
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_order_detail_api_authenticated_owner(self):
        """Test order detail API endpoint with authenticated owner"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('store_api:order_detail', kwargs={'pk': self.order.pk})
        response = self.client.get(url)
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.id)
    
    def test_order_detail_api_authenticated_non_owner(self):
        """Test order detail API endpoint with authenticated non-owner"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.client.force_authenticate(user=other_user)
        
        url = reverse('store_api:order_detail', kwargs={'pk': self.order.pk})
        response = self.client.get(url)
        
        # Verify response - should be 404 as user can't access other's orders
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class UserAPITestCase(TestCase):
    """Test cases for user profile API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_profile_api_authenticated(self):
        """Test user profile API endpoint with authentication"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('store_api:user_profile')
        response = self.client.get(url)
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['first_name'], 'Test')
        self.assertEqual(response.data['last_name'], 'User')
    
    def test_user_profile_api_unauthenticated(self):
        """Test user profile API endpoint without authentication"""
        url = reverse('store_api:user_profile')
        response = self.client.get(url)
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class CartAPITestCase(TestCase):
    """Test cases for cart API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
    
    def test_cart_api_get(self):
        """Test cart API GET endpoint"""
        url = reverse('store_api:cart')
        response = self.client.get(url)
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        self.assertIn('total', response.data)
    
    def test_cart_api_post(self):
        """Test cart API POST endpoint"""
        url = reverse('store_api:cart')
        data = {
            'product_id': 1,
            'quantity': 2
        }
        response = self.client.post(url, data)
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Item added to cart')