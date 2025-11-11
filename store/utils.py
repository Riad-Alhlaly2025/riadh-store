from PIL import Image
import os
from django.conf import settings

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