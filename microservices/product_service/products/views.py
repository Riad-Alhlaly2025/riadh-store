from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg
from django.core.cache import cache
from .models import Product, Category, Brand, ProductReview
from .serializers import ProductSerializer, ProductListSerializer, CategorySerializer, BrandSerializer, ProductReviewSerializer

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]

class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(seo_keywords__icontains=search)
            )
        
        # Category filter
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Brand filter
        brand = self.request.query_params.get('brand', None)
        if brand:
            queryset = queryset.filter(brand__id=brand)
        
        # Price range filters
        min_price = self.request.query_params.get('min_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = self.request.query_params.get('max_price', None)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Sorting
        sort_by = self.request.query_params.get('sort_by', 'created_at')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'rating':
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).order_by('-avg_rating')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        # Try to get from cache first
        product_id = self.kwargs['pk']
        cache_key = f'product_detail_{product_id}'
        product = cache.get(cache_key)
        
        if product is None:
            product = get_object_or_404(Product, pk=product_id, is_active=True)
            # Cache for 30 minutes
            cache.set(cache_key, product, 60 * 30)
        
        return product

@api_view(['GET'])
@permission_classes([AllowAny])
def product_search(request):
    """Search products with advanced filtering"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    brand = request.GET.get('brand', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort_by', 'relevance')
    
    # Start with active products
    products = Product.objects.filter(is_active=True)
    
    # Apply search query
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(seo_keywords__icontains=query)
        )
    
    # Apply category filter
    if category:
        products = products.filter(category=category)
    
    # Apply brand filter
    if brand:
        products = products.filter(brand__id=brand)
    
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
    elif sort_by == 'rating':
        products = products.annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')
    else:
        # Default sorting by relevance (created_at for now)
        products = products.order_by('-created_at')
    
    # Serialize results
    serializer = ProductListSerializer(products, many=True)
    return Response({
        'results': serializer.data,
        'count': products.count(),
        'query': query,
        'filters': {
            'category': category,
            'brand': brand,
            'min_price': min_price,
            'max_price': max_price,
            'sort_by': sort_by
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product_review(request, product_id):
    """Add a review to a product"""
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if user already reviewed this product
    if ProductReview.objects.filter(product=product, user=request.user).exists():
        return Response(
            {'error': 'You have already reviewed this product'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = ProductReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(product=product, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def featured_products(request):
    """Get featured products"""
    # For now, we'll return products with highest ratings
    # In a real implementation, you might have a featured flag
    products = Product.objects.filter(is_active=True).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-avg_rating')[:10]
    
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)