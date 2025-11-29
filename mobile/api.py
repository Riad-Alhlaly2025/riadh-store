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
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
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
    """Get home screen data for mobile app with optimized queries"""
    Product = apps.get_model('store', 'Product')
    Order = apps.get_model('store', 'Order')
    Category = apps.get_model('store', 'Category')  # If you have a Category model
    
    # Get featured products with optimized queries
    featured_products = Product.objects.select_related(
        'seller'
    ).filter(is_featured=True)[:10]
    
    # Get categories
    categories = Product.objects.values('category').distinct()[:8]
    
    # Get banners/offers (you might want to create a Banner model)
    banners = []
    
    # Get trending products based on recent orders
    thirty_days_ago = timezone.now() - timedelta(days=30)
    trending_products = Product.objects.select_related(
        'seller'
    ).filter(
        orderitem__order__created_at__gte=thirty_days_ago
    ).annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')[:10]
    
    data = {
        'banners': banners,
        'featured_products': MobileProductSerializer(featured_products, many=True).data,
        'trending_products': MobileProductSerializer(trending_products, many=True).data,
        'categories': [{'name': cat['category']} for cat in categories],
        'offers': []  # Add offers logic here
    }
    
    return Response(data)

@api_view(['GET'])
@permission_classes([AllowAny])
def mobile_product_list(request):
    """Get paginated product list for mobile app with optimized queries"""
    Product = apps.get_model('store', 'Product')
    
    # Get query parameters
    page = int(request.GET.get('page', 1))
    category = request.GET.get('category', '')
    sort_by = request.GET.get('sort_by', 'name')
    search_query = request.GET.get('search', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    # Filter products with optimized queries
    products = Product.objects.select_related('seller')
    
    # Apply search query
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    if category:
        products = products.filter(category=category)
    
    # Apply price filters
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Apply sorting
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'popularity':
        products = products.annotate(
            order_count=Count('orderitem')
        ).order_by('-order_count')
    elif sort_by == 'rating':
        # This would require a review system
        products = products.order_by('-created_at')
    
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
    """Get product details for mobile app with optimized queries"""
    Product = apps.get_model('store', 'Product')
    OrderItem = apps.get_model('store', 'OrderItem')
    
    try:
        product = Product.objects.select_related(
            'seller'
        ).prefetch_related(
            'orderitem_set'
        ).get(id=product_id)
        
        # Get related products
        related_products = Product.objects.select_related(
            'seller'
        ).filter(
            category=product.category
        ).exclude(
            id=product.id
        )[:5]
        
        serializer = MobileProductSerializer(product)
        related_serializer = MobileProductSerializer(related_products, many=True)
        
        # Add related products to response
        response_data = serializer.data
        response_data['related_products'] = related_serializer.data
        
        return Response(response_data)
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
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
    
    elif request.method == 'PUT':
        # Update cart item quantity
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        # Add logic to update item quantity
        return Response(
            {'message': 'Cart item updated'}, 
            status=status.HTTP_200_OK
        )
    
    elif request.method == 'DELETE':
        # Remove item from cart
        product_id = request.data.get('product_id')
        
        # Add logic to remove item from cart
        return Response(
            {'message': 'Item removed from cart'}, 
            status=status.HTTP_204_NO_CONTENT
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_user_profile(request):
    """Get user profile for mobile app"""
    serializer = MobileUserSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_user_profile(request):
    """Get user profile for mobile app"""
    serializer = MobileUserSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_user_dashboard(request):
    """Get user dashboard data for mobile app"""
    # Import models
    Product = apps.get_model('store', 'Product')
    Order = apps.get_model('store', 'Order')
    OrderItem = apps.get_model('store', 'OrderItem')
    
    # Get user statistics
    user_orders = Order.objects.filter(user=request.user)
    total_orders = user_orders.count()
    pending_orders = user_orders.filter(status='pending').count()
    
    # Get recent orders with optimized queries
    recent_orders = user_orders.select_related(
        'user'
    ).prefetch_related(
        'items', 'items__product'
    ).order_by('-created_at')[:5]
    
    # Get user's favorite products (simulated)
    favorite_products = Product.objects.select_related(
        'seller'
    ).filter(is_featured=True)[:5]
    
    data = {
        'statistics': {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
        },
        'recent_orders': MobileOrderSerializer(recent_orders, many=True).data,
        'favorite_products': MobileProductSerializer(favorite_products, many=True).data,
    }
    
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_user_orders(request):
    """Get user orders for mobile app with optimized queries"""
    Order = apps.get_model('store', 'Order')
    OrderItem = apps.get_model('store', 'OrderItem')
    
    orders = Order.objects.select_related(
        'user'
    ).prefetch_related(
        'items', 'items__product'
    ).filter(user=request.user).order_by('-created_at')
    serializer = MobileOrderSerializer(orders, many=True)
    
    return Response(serializer.data)