"""
Unit tests for image optimization functionality
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.apps import apps
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
import os
import tempfile
from unittest.mock import patch, MagicMock
from PIL import Image
import io

class ImageOptimizationUtilsTestCase(TestCase):
    """Test cases for image optimization utilities"""
    
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
    
    def test_create_responsive_sizes(self):
        """Test creating responsive image sizes"""
        from store.utils import create_responsive_sizes
        
        # Create a test image in memory
        img = Image.new('RGB', (1200, 900), color='red')
        
        # Create a temporary file path
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            temp_path = tmp.name
        
        try:
            # Save the image
            img.save(temp_path, 'JPEG')
            
            # Test creating responsive sizes
            create_responsive_sizes(img, temp_path, quality=85)
            
            # Check that responsive size files were created
            base_name = os.path.splitext(temp_path)[0]
            
            # Check for 320w version
            small_jpg = f"{base_name}_320w.jpg"
            small_webp = f"{base_name}_320w.webp"
            self.assertTrue(os.path.exists(small_jpg))
            self.assertTrue(os.path.exists(small_webp))
            
            # Check for 640w version
            medium_jpg = f"{base_name}_640w.jpg"
            medium_webp = f"{base_name}_640w.webp"
            self.assertTrue(os.path.exists(medium_jpg))
            self.assertTrue(os.path.exists(medium_webp))
            
            # Check for 1200w version (should not exist as it's the same size as original)
            large_jpg = f"{base_name}_1200w.jpg"
            large_webp = f"{base_name}_1200w.webp"
            self.assertFalse(os.path.exists(large_jpg))
            self.assertFalse(os.path.exists(large_webp))
            
        finally:
            # Clean up test files
            files_to_remove = [
                temp_path,
                f"{base_name}_320w.jpg",
                f"{base_name}_320w.webp",
                f"{base_name}_640w.jpg",
                f"{base_name}_640w.webp"
            ]
            
            for file_path in files_to_remove:
                if os.path.exists(file_path):
                    os.remove(file_path)
    
    def test_optimize_image_with_jpeg(self):
        """Test optimizing a JPEG image"""
        from store.utils import optimize_image
        
        # Create a test JPEG image in memory
        img = Image.new('RGB', (800, 600), color='blue')
        
        # Create a temporary file path
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            temp_path = tmp.name
        
        try:
            # Save the original image
            img.save(temp_path, 'JPEG')
            
            # Get original file size
            original_size = os.path.getsize(temp_path)
            
            # Optimize the image
            optimize_image(temp_path, max_width=400, max_height=300, quality=80)
            
            # Get optimized file size
            optimized_size = os.path.getsize(temp_path)
            
            # Check that file size is smaller (or equal in some edge cases)
            self.assertLessEqual(optimized_size, original_size)
            
            # Check that WebP version was created
            webp_path = os.path.splitext(temp_path)[0] + '.webp'
            self.assertTrue(os.path.exists(webp_path))
            
            # Check that responsive sizes were created
            base_name = os.path.splitext(temp_path)[0]
            small_jpg = f"{base_name}_320w.jpg"
            self.assertTrue(os.path.exists(small_jpg))
            
        finally:
            # Clean up test files
            files_to_remove = [
                temp_path,
                os.path.splitext(temp_path)[0] + '.webp',
                f"{os.path.splitext(temp_path)[0]}_320w.jpg",
                f"{os.path.splitext(temp_path)[0]}_640w.jpg"
            ]
            
            for file_path in files_to_remove:
                if os.path.exists(file_path):
                    os.remove(file_path)
    
    def test_optimize_image_with_png_transparency(self):
        """Test optimizing a PNG image with transparency"""
        from store.utils import optimize_image
        
        # Create a test PNG image with transparency
        img = Image.new('RGBA', (400, 300), color=(255, 0, 0, 128))  # Semi-transparent red
        
        # Create a temporary file path
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            temp_path = tmp.name
        
        try:
            # Save the original image
            img.save(temp_path, 'PNG')
            
            # Optimize the image
            optimize_image(temp_path, max_width=200, max_height=150, quality=75)
            
            # Check that WebP version was created
            webp_path = os.path.splitext(temp_path)[0] + '.webp'
            self.assertTrue(os.path.exists(webp_path))
            
        finally:
            # Clean up test files
            files_to_remove = [
                temp_path,
                os.path.splitext(temp_path)[0] + '.webp',
                f"{os.path.splitext(temp_path)[0]}_320w.jpg",
                f"{os.path.splitext(temp_path)[0]}_640w.jpg"
            ]
            
            for file_path in files_to_remove:
                if os.path.exists(file_path):
                    os.remove(file_path)
    
    def test_optimize_product_images(self):
        """Test optimizing all product images"""
        from store.utils import optimize_product_images
        
        # Create a temporary directory structure
        media_root = settings.MEDIA_ROOT
        products_dir = os.path.join(media_root, 'products')
        
        # Ensure products directory exists
        os.makedirs(products_dir, exist_ok=True)
        
        # Create test images
        test_images = []
        for i in range(3):
            img = Image.new('RGB', (800, 600), color=f'rgb({i*50}, {i*50}, {i*50})')
            
            # Create temporary file paths
            jpg_path = os.path.join(products_dir, f'test_image_{i}.jpg')
            png_path = os.path.join(products_dir, f'test_image_{i}.png')
            
            # Save images
            img.save(jpg_path, 'JPEG')
            img.save(png_path, 'PNG')
            
            test_images.extend([jpg_path, png_path])
        
        try:
            # Mock the optimize_image function to avoid actual optimization
            with patch('store.utils.optimize_image') as mock_optimize:
                # Call optimize_product_images
                optimize_product_images()
                
                # Check that optimize_image was called for each image
                self.assertEqual(mock_optimize.call_count, 6)  # 3 JPG + 3 PNG
                
        finally:
            # Clean up test files
            for image_path in test_images:
                if os.path.exists(image_path):
                    os.remove(image_path)

class ImageOptimizationViewsTestCase(TestCase):
    """Test cases for image optimization views"""
    
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
    
    def test_optimize_images_view_get(self):
        """Test accessing optimize images view with GET request"""
        # Login as manager
        self.client.login(username='manager', password='testpass123')
        
        response = self.client.get(reverse('optimize_images'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/optimize_images.html')
    
    @patch('store.views.optimize_product_images')
    def test_optimize_images_view_post_success(self, mock_optimize):
        """Test optimizing images with POST request - success case"""
        # Mock successful optimization
        mock_optimize.return_value = None  # Function doesn't return anything
        
        # Login as manager
        self.client.login(username='manager', password='testpass123')
        
        # Post to optimize images
        response = self.client.post(reverse('optimize_images'))
        
        # Check that optimization function was called
        mock_optimize.assert_called_once()
        
        # Check that we were redirected (or re-rendered the same page)
        self.assertEqual(response.status_code, 200)
        
        # Check for success message
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'success')
    
    @patch('store.views.optimize_product_images')
    def test_optimize_images_view_post_failure(self, mock_optimize):
        """Test optimizing images with POST request - failure case"""
        # Mock failed optimization
        mock_optimize.side_effect = Exception('Optimization failed')
        
        # Login as manager
        self.client.login(username='manager', password='testpass123')
        
        # Post to optimize images
        response = self.client.post(reverse('optimize_images'))
        
        # Check that optimization function was called
        mock_optimize.assert_called_once()
        
        # Check for error message
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertIn('حدث خطأ أثناء تحسين الصور', messages[0].message)
    
    def test_optimize_images_view_requires_login(self):
        """Test that optimize images view requires login"""
        response = self.client.get(reverse('optimize_images'))
        self.assertEqual(response.status_code, 302)  # Redirect to login