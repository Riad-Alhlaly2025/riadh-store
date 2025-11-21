from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from django.apps import apps
from datetime import datetime, timedelta


class AnalyticsTestCase(TestCase):
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
        Commission = apps.get_model('store', 'Commission')
        AnalyticsIntegration = apps.get_model('store', 'AnalyticsIntegration')
        
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
            phone_number='123456789',
            status='delivered'
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
        
        # Create commissions
        self.seller_commission = Commission.objects.create(
            user=self.seller_user,
            order=self.order,
            amount=Decimal('15.00'),
            rate=Decimal('10.00'),
            is_paid=False
        )
        self.buyer_commission = Commission.objects.create(
            user=self.buyer_user,
            order=self.order,
            amount=Decimal('3.00'),
            rate=Decimal('2.00'),
            is_paid=False
        )
        
        # Create analytics events
        thirty_days_ago = datetime.now() - timedelta(days=30)
        self.analytics_event1 = AnalyticsIntegration.objects.create(
            user=self.buyer_user,
            event_type='page_view',
            url='https://test-store.com/',
            timestamp=thirty_days_ago
        )
        self.analytics_event2 = AnalyticsIntegration.objects.create(
            user=self.buyer_user,
            event_type='product_view',
            product=self.product1,
            url='https://test-store.com/product/1/',
            timestamp=thirty_days_ago + timedelta(days=1)
        )
        self.analytics_event3 = AnalyticsIntegration.objects.create(
            user=self.buyer_user,
            event_type='add_to_cart',
            product=self.product1,
            url='https://test-store.com/product/1/',
            timestamp=thirty_days_ago + timedelta(days=2)
        )
        self.analytics_event4 = AnalyticsIntegration.objects.create(
            user=self.buyer_user,
            event_type='checkout',
            order=self.order,
            url='https://test-store.com/checkout/',
            timestamp=thirty_days_ago + timedelta(days=3)
        )
        self.analytics_event5 = AnalyticsIntegration.objects.create(
            user=self.buyer_user,
            event_type='purchase',
            order=self.order,
            url='https://test-store.com/payment/',
            timestamp=thirty_days_ago + timedelta(days=4)
        )

    def test_ai_analytics_dashboard_view(self):
        """Test that the AI analytics dashboard view works correctly"""
        # Login as manager
        self.client.login(username='manager', password='testpass123')
        
        # Access the AI analytics dashboard
        response = self.client.get(reverse('ai_analytics_dashboard'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the template is correct
        self.assertTemplateUsed(response, 'store/ai_analytics_dashboard.html')
        
        # Check that context data is present
        self.assertIn('total_products', response.context)
        self.assertIn('total_orders', response.context)
        self.assertIn('total_users', response.context)
        self.assertIn('total_revenue', response.context)
        self.assertIn('category_sales', response.context)
        self.assertIn('top_products_by_quantity', response.context)
        self.assertIn('top_products_by_revenue', response.context)
        
        # Check some specific values
        self.assertEqual(response.context['total_products'], 2)
        self.assertEqual(response.context['total_orders'], 1)
        self.assertEqual(response.context['total_users'], 3)
        self.assertEqual(response.context['total_revenue'], Decimal('150.00'))

    def test_analytics_integration_view(self):
        """Test that the analytics integration view works correctly"""
        # Login as manager
        self.client.login(username='manager', password='testpass123')
        
        # Access the analytics integration view
        response = self.client.get(reverse('analytics_integration'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the template is correct
        self.assertTemplateUsed(response, 'store/analytics_integration.html')
        
        # Check that context data is present
        self.assertIn('total_events', response.context)
        self.assertIn('event_types', response.context)
        self.assertIn('analytics_events', response.context)
        
        # Check some specific values
        self.assertEqual(response.context['total_events'], 5)

    def test_export_analytics_report_csv(self):
        """Test that the analytics report can be exported as CSV"""
        # Login as manager
        self.client.login(username='manager', password='testpass123')
        
        # Access the export view
        response = self.client.get(reverse('export_analytics_report', kwargs={'format': 'csv'}))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the content type is CSV
        self.assertEqual(response['Content-Type'], 'text/csv')
        
        # Check that the content disposition is correct
        self.assertIn('attachment;', response['Content-Disposition'])
        self.assertIn('filename="analytics_report.csv"', response['Content-Disposition'])

    def test_advanced_search_view(self):
        """Test that the advanced search view works correctly"""
        # Access the advanced search view
        response = self.client.get(reverse('advanced_search'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the template is correct
        self.assertTemplateUsed(response, 'store/advanced_search.html')
        
        # Check that context data is present
        self.assertIn('products', response.context)
        self.assertIn('categories', response.context)
        self.assertIn('price_range', response.context)

    def test_advanced_search_with_query(self):
        """Test that the advanced search works with a query"""
        # Search for "Test Product 1"
        response = self.client.get(reverse('advanced_search'), {'q': 'Test Product 1'})
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that only one product is returned
        self.assertEqual(len(response.context['products']), 1)
        self.assertEqual(response.context['products'][0].name, 'Test Product 1')

    def test_advanced_search_with_category_filter(self):
        """Test that the advanced search works with category filter"""
        # Search for products in the 'phones' category
        response = self.client.get(reverse('advanced_search'), {'category': 'phones'})
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that only one product is returned
        self.assertEqual(len(response.context['products']), 1)
        self.assertEqual(response.context['products'][0].category, 'phones')

    def test_advanced_search_with_price_filter(self):
        """Test that the advanced search works with price filters"""
        # Search for products with price between 40 and 60
        response = self.client.get(reverse('advanced_search'), {
            'min_price': '40',
            'max_price': '60'
        })
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that only one product is returned
        self.assertEqual(len(response.context['products']), 1)
        self.assertEqual(response.context['products'][0].name, 'Test Product 2')
        self.assertEqual(response.context['products'][0].price, Decimal('50.00'))

    def test_advanced_search_with_sorting(self):
        """Test that the advanced search works with sorting"""
        # Search and sort by price ascending
        response = self.client.get(reverse('advanced_search'), {'sort_by': 'price_asc'})
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that products are sorted correctly
        products = response.context['products']
        self.assertEqual(len(products), 2)
        self.assertTrue(products[0].price <= products[1].price)
        
        # Search and sort by price descending
        response = self.client.get(reverse('advanced_search'), {'sort_by': 'price_desc'})
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that products are sorted correctly
        products = response.context['products']
        self.assertEqual(len(products), 2)
        self.assertTrue(products[0].price >= products[1].price)