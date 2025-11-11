from django.core.management.base import BaseCommand
from django.apps import apps
from decimal import Decimal
from store.amazon_api import AmazonProductAPI

class Command(BaseCommand):
    help = 'Import products from Amazon API'

    def add_arguments(self, parser):
        parser.add_argument('keywords', type=str, help='Search keywords for Amazon products')
        parser.add_argument('--count', type=int, default=10, help='Number of products to import')
        parser.add_argument('--category', type=str, default='Electronics', help='Amazon category to search in')

    def handle(self, *args, **options):
        keywords = options['keywords']
        count = options['count']
        category = options['category']
        
        self.stdout.write(f'Importing {count} products from Amazon with keywords: {keywords}')
        
        # Initialize Amazon API
        amazon_api = AmazonProductAPI()
        
        # Search for products
        products = amazon_api.search_products(keywords, category, count)
        
        if not products:
            self.stdout.write(
                self.style.WARNING('No products found or error occurred')
            )
            return
        
        # Get Product model
        Product = apps.get_model('store', 'Product')
        
        # Import products
        imported_count = 0
        for amazon_product in products:
            try:
                # Check if product already exists
                asin = amazon_product['asin']
                if Product.objects.filter(description__icontains=asin).exists():
                    self.stdout.write(
                        f'Skipping existing product: {amazon_product["title"][:50]}...'
                    )
                    continue
                
                # Create product
                price = Decimal(amazon_product['price']) / 100 if amazon_product['price'] else Decimal('0.00')
                
                product = Product.objects.create(
                    name=amazon_product['title'][:100],  # Truncate to fit field limit
                    price=price,
                    description=f"ASIN: {asin}\n{amazon_product.get('description', 'No description available')}",
                    image_url=amazon_product['image_url'],
                    category='electronics',  # Map to your category system
                    currency=amazon_product['currency'][:3] if amazon_product['currency'] else 'USD',
                    seo_title=amazon_product['title'][:60],
                    seo_description=amazon_product['title'][:160],
                )
                
                imported_count += 1
                self.stdout.write(
                    f'Imported: {product.name[:50]}...'
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error importing product {amazon_product["title"][:30]}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {imported_count} products from Amazon')
        )