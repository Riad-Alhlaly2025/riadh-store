from django.core.management.base import BaseCommand
from store.utils import optimize_product_images

class Command(BaseCommand):
    help = 'Optimize all product images'

    def handle(self, *args, **options):
        self.stdout.write('Optimizing product images...')
        optimize_product_images()
        # Using SUCCESS style constant directly
        success_style = getattr(self.style, 'SUCCESS', lambda x: x)
        self.stdout.write(success_style('Successfully optimized all product images'))