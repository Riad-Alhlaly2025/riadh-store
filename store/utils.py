from PIL import Image
import os
from django.conf import settings
from django.apps import apps


class CartItem:
    def __init__(self, product, quantity=1):
        self.product = product
        self.quantity = quantity
    
    @property
    def total_price(self):
        return self.product.price * self.quantity


class Cart:
    def __init__(self, session):
        self.session = session
        self.cart = session.get('cart', {})
    
    def add(self, product_id, quantity=1):
        """Add a product to the cart"""
        product_id = str(product_id)
        quantity = int(quantity)
        if product_id in self.cart:
            self.cart[product_id] += quantity
        else:
            self.cart[product_id] = quantity
        self.save()
    
    def remove(self, product_id):
        """Remove a product from the cart"""
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def update(self, product_id, quantity):
        """Update the quantity of a product in the cart"""
        product_id = str(product_id)
        quantity = int(quantity)
        if quantity > 0:
            self.cart[product_id] = quantity
        elif product_id in self.cart:
            del self.cart[product_id]
        self.save()
    
    def save(self):
        """Save the cart to the session"""
        self.session['cart'] = self.cart
        self.session.modified = True
    
    def clear(self):
        """Remove all items from the cart"""
        self.cart = {}
        self.save()
    
    def get_items(self):
        """Get cart items with product details"""
        Product = apps.get_model('store', 'Product')
        items = []
        # Create a copy of the cart items to avoid modification during iteration
        cart_items = list(self.cart.items())
        for product_id, quantity in cart_items:
            try:
                product = Product.objects.get(pk=product_id)
                items.append({
                    'product': product,
                    'quantity': int(quantity),
                    'total_price': product.price * int(quantity),
                    'id': product_id
                })
            except (Product.DoesNotExist, ValueError, TypeError):
                # Remove invalid product from cart
                self.remove(product_id)
        return items
    
    def get_total_price(self):
        """Calculate the total price of all items in the cart"""
        total = 0
        for item in self.get_items():
            total += item['total_price']
        return total
    
    def get_total_quantity(self):
        """Calculate the total quantity of all items in the cart"""
        try:
            return sum(int(quantity) for quantity in self.cart.values())
        except (ValueError, TypeError):
            # If there are any invalid quantities, return 0
            return 0

def optimize_image(image_path, max_width=800, max_height=600, quality=85):
    """
    Optimize an image by resizing and compressing it.
    """
    if not os.path.exists(image_path):
        return
    
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Calculate new dimensions maintaining aspect ratio
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
    except Exception as e:
        print(f"Error optimizing image {image_path}: {e}")

def optimize_product_images():
    """
    Optimize all product images in the media directory.
    """
    media_root = settings.MEDIA_ROOT
    products_dir = os.path.join(media_root, 'products')
    
    if not os.path.exists(products_dir):
        return
    
    for filename in os.listdir(products_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(products_dir, filename)
            optimize_image(image_path)