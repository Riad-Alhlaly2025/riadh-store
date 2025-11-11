from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection
from django.db.models import Count, Avg, Sum
from decimal import Decimal

class Command(BaseCommand):
    help = 'Analyze database performance and generate reports'

    def handle(self, *args, **options):
        self.stdout.write('Analyzing database performance...')
        
        # Get models
        Product = apps.get_model('store', 'Product')
        Order = apps.get_model('store', 'Order')
        OrderItem = apps.get_model('store', 'OrderItem')
        Payment = apps.get_model('store', 'Payment')
        Commission = apps.get_model('store', 'Commission')
        User = apps.get_model('auth', 'User')
        
        # Product analysis
        total_products = Product.objects.count()
        products_by_category = Product.objects.values('category').annotate(count=Count('id'))
        
        self.stdout.write('\n=== PRODUCT ANALYSIS ===')
        self.stdout.write(f'Total products: {total_products}')
        self.stdout.write('Products by category:')
        for category in products_by_category:
            self.stdout.write(f"  {category['category']}: {category['count']}")
        
        # Order analysis
        total_orders = Order.objects.count()
        orders_by_status = Order.objects.values('status').annotate(count=Count('id'))
        avg_order_value = Order.objects.aggregate(avg_value=Avg('total_amount'))['avg_value']
        
        self.stdout.write('\n=== ORDER ANALYSIS ===')
        self.stdout.write(f'Total orders: {total_orders}')
        self.stdout.write(f'Average order value: {avg_order_value or 0:.2f}')
        self.stdout.write('Orders by status:')
        for status in orders_by_status:
            self.stdout.write(f"  {status['status']}: {status['count']}")
        
        # Payment analysis
        total_payments = Payment.objects.count()
        payments_by_method = Payment.objects.values('payment_method').annotate(count=Count('id'))
        total_payment_amount = Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        self.stdout.write('\n=== PAYMENT ANALYSIS ===')
        self.stdout.write(f'Total payments: {total_payments}')
        self.stdout.write(f'Total payment amount: {total_payment_amount:.2f}')
        self.stdout.write('Payments by method:')
        for method in payments_by_method:
            self.stdout.write(f"  {method['payment_method']}: {method['count']}")
        
        # Commission analysis
        total_commissions = Commission.objects.count()
        total_commission_amount = Commission.objects.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        avg_commission_rate = Commission.objects.aggregate(
            avg_rate=Avg('rate')
        )['avg_rate'] or Decimal('0.00')
        
        self.stdout.write('\n=== COMMISSION ANALYSIS ===')
        self.stdout.write(f'Total commissions: {total_commissions}')
        self.stdout.write(f'Total commission amount: {total_commission_amount:.2f}')
        self.stdout.write(f'Average commission rate: {avg_commission_rate:.2f}%')
        
        # User analysis
        total_users = User.objects.count()
        users_with_orders = Order.objects.values('user').distinct().count()
        
        self.stdout.write('\n=== USER ANALYSIS ===')
        self.stdout.write(f'Total users: {total_users}')
        self.stdout.write(f'Users with orders: {users_with_orders}')
        self.stdout.write(f'Conversion rate: {(users_with_orders/total_users*100) if total_users > 0 else 0:.2f}%')
        
        # Database query analysis
        self.stdout.write('\n=== DATABASE PERFORMANCE ===')
        self.stdout.write(f'Total database queries executed: {len(connection.queries)}')
        
        # Show slowest queries if DEBUG is True
        if connection.queries:
            # Sort queries by execution time (if available)
            slowest_queries = sorted(
                [q for q in connection.queries if 'time' in q], 
                key=lambda x: float(x['time']), 
                reverse=True
            )[:5]
            
            self.stdout.write('Slowest queries:')
            for i, query in enumerate(slowest_queries, 1):
                self.stdout.write(f"  {i}. {query['time']}s - {query['sql'][:100]}...")
        
        self.stdout.write(
            self.style.SUCCESS('\nDatabase performance analysis completed')
        )