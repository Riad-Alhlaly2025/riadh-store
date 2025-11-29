from django.apps import apps
from django.contrib.auth.models import User

# Get models
SocialMediaIntegration = apps.get_model('store', 'SocialMediaIntegration')
Product = apps.get_model('store', 'Product')

# Create test user and product
user = User.objects.create_user(username='testuser', password='testpass')
product = Product.objects.create(
    name='Test Product', 
    description='Test Description', 
    price=10.0, 
    stock_quantity=5, 
    category='Electronics', 
    seller=user
)

# Create first integration
integration1 = SocialMediaIntegration.objects.create(
    product=product, 
    platform='facebook', 
    status='pending'
)
print('First integration created:', integration1.id)

# Try to create second integration with same product and platform
try:
    integration2 = SocialMediaIntegration.objects.create(
        product=product, 
        platform='facebook', 
        status='pending'
    )
    print('Second integration created:', integration2.id)
except Exception as e:
    print('Error creating second integration:', str(e))