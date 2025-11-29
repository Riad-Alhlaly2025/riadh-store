"""
Mobile API for MyShop e-commerce platform
This module provides RESTful endpoints specifically designed for mobile applications
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.apps import apps
from django.core.paginator import Paginator
from .serializers import (
    MobileProductSerializer,
    MobileCategorySerializer,
    MobileCartSerializer,
    MobileOrderSerializer,
    MobileUserSerializer
)

@api_view(['GET'])
@permission_classes([AllowAny])
def mobile_home_data(request):
    """Get home screen data for mobile app"""
    Product = apps.get_model('store', 'Product')
    Category = apps.get_model('store', 'Category')  # If you have a Category model
    
    # Get featured products
    featured_products = Product.objects.filter(is_featured=True)[:10]
    
    # Get categories
    categories = Product.objects.values('category').distinct()[:8]
    
    # Get banners/offers (you might want to create a Banner model)
    banners = []
    
    data = {
        'banners': banners,
        'featured_products': MobileProductSerializer(featured_products, many=True).data,
        'categories': [{'name': cat['category']} for cat in categories],
        'offers': []  # Add offers logic here
    }
    
    return Response(data)

@api_view(['GET'])
@permission_classes([AllowAny])
def mobile_product_list(request):
    """Get paginated product list for mobile app"""
    Product = apps.get_model('store', 'Product')
    
    # Get query parameters
    page = int(request.GET.get('page', 1))
    category = request.GET.get('category', '')
    sort_by = request.GET.get('sort_by', 'name')
    
    # Filter products
    products = Product.objects.all()
    
    if category:
        products = products.filter(category=category)
    
    # Apply sorting
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    
    # Paginate results
    paginator = Paginator(products, 20)  # 20 products per page
    page_obj = paginator.get_page(page)
    
    serializer = MobileProductSerializer(page_obj, many=True)
    
    return Response({
        'products': serializer.data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def mobile_product_detail(request, product_id):
    """Get product details for mobile app"""
    Product = apps.get_model('store', 'Product')
    
    try:
        product = Product.objects.get(id=product_id)
        serializer = MobileProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def mobile_cart(request):
    """Manage shopping cart for mobile app"""
    if request.method == 'GET':
        # Return cart contents
        cart_data = {
            'items': [],
            'total': 0,
            'item_count': 0
        }
        serializer = MobileCartSerializer(cart_data)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Add/update cart item
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        # Add logic to add item to cart
        return Response(
            {'message': 'Item added to cart'}, 
            status=status.HTTP_201_CREATED
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_user_profile(request):
    """Get user profile for mobile app"""
    serializer = MobileUserSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_user_orders(request):
    """Get user orders for mobile app"""
    Order = apps.get_model('store', 'Order')
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = MobileOrderSerializer(orders, many=True)
    
    return Response(serializer.data)