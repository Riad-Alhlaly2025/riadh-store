from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection
from django.utils import timezone
import time
import psutil
import os

class Command(BaseCommand):
    help = 'Monitor system performance and log metrics'

    def add_arguments(self, parser):
        parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in seconds')
        parser.add_argument('--duration', type=int, default=3600, help='Monitoring duration in seconds')

    def handle(self, *args, **options):
        interval = options['interval']
        duration = options['duration']
        
        self.stdout.write(f'Starting performance monitoring for {duration} seconds (interval: {interval}s)')
        
        start_time = time.time()
        end_time = start_time + duration
        
        # Get initial process info
        process = psutil.Process(os.getpid())
        
        while time.time() < end_time:
            # Collect metrics
            timestamp = timezone.now()
            
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            disk_usage = psutil.disk_usage('/')
            
            # Process metrics
            process_cpu = process.cpu_percent()
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Database metrics
            db_queries = len(connection.queries)
            
            # Django model counts
            Product = apps.get_model('store', 'Product')
            Order = apps.get_model('store', 'Order')
            User = apps.get_model('auth', 'User')
            
            product_count = Product.objects.count()
            order_count = Order.objects.count()
            user_count = User.objects.count()
            
            # Log metrics
            self.stdout.write(
                f"[{timestamp}] "
                f"CPU: {cpu_percent:.1f}% | "
                f"Memory: {memory_info.percent:.1f}% | "
                f"Process CPU: {process_cpu:.1f}% | "
                f"Process Memory: {process_memory:.1f}MB | "
                f"DB Queries: {db_queries} | "
                f"Products: {product_count} | "
                f"Orders: {order_count} | "
                f"Users: {user_count}"
            )
            
            # Wait for next interval
            time.sleep(interval)
        
        self.stdout.write(
            self.style.SUCCESS('Performance monitoring completed')
        )