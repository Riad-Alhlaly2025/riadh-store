from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.apps import apps
from django.utils import timezone

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        Product = apps.get_model('store', 'Product')
        return Product.objects.all()

    def lastmod(self, obj):
        # Return a default date since Product model doesn't have a date field
        # In a real scenario, you might want to add a created_at or updated_at field to Product model
        return timezone.now()

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return ['home', 'product_list']

    def location(self, item):
        return reverse(item)