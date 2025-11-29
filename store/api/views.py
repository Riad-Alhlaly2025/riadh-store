from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.apps import apps
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum, Prefetch
from .serializers import (
    ProductSerializer, 
    CategorySerializer, 
    CartSerializer, 
    OrderSerializer, 
    UserProfileSerializer
)

class ProductListView(generics.ListAPIView):
    """List all products with optimized queries and filtering"""
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        Product = apps.get_model('store', 'Product')
        OrderItem = apps.get_model('store', 'OrderItem')
        
        # Start with optimized query
        queryset = Product.objects.select_related('seller')
        
        # Apply filters from query parameters
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        min_price = self.request.query_params.get('min_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = self.request.query_params.get('max_price', None)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Apply sorting
        sort_by = self.request.query_params.get('sort_by', 'name')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'popularity':
            queryset = queryset.annotate(
                order_count=Count('orderitem')
            ).order_by('-order_count')
        else:
            queryset = queryset.order_by('name')
        
        return queryset

class ProductDetailView(generics.RetrieveAPIView):
    """Retrieve a specific product with optimized queries"""
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        Product = apps.get_model('store', 'Product')
        OrderItem = apps.get_model('store', 'OrderItem')
        
        return Product.objects.select_related(
            'seller'
        ).prefetch_related(
            Prefetch(
                'orderitem_set',
                queryset=OrderItem.objects.select_related('order')
            )
        )

class CategoryListView(generics.ListAPIView):
    """List all categories"""
    serializer_class = CategorySerializer
    
    def get_queryset(self):
        Product = apps.get_model('store', 'Product')
        return Product.objects.values('category').distinct()

class CartView(APIView):
    """Manage shopping cart"""
    def get(self, request):
        # Return cart contents
        cart_data = {
            'items': [],
            'total': 0
        }
        serializer = CartSerializer(cart_data)
        return Response(serializer.data)
    
    def post(self, request):
        # Add item to cart
        return Response({'message': 'Item added to cart'}, status=status.HTTP_201_CREATED)
    
    def put(self, request):
        # Update cart item
        return Response({'message': 'Cart updated'}, status=status.HTTP_200_OK)
    
    def delete(self, request):
        # Clear cart
        return Response({'message': 'Cart cleared'}, status=status.HTTP_204_NO_CONTENT)

class OrderListView(generics.ListAPIView):
    """List user orders with optimized queries"""
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        Order = apps.get_model('store', 'Order')
        OrderItem = apps.get_model('store', 'OrderItem')
        
        if self.request.user.is_authenticated:
            return Order.objects.select_related(
                'user'
            ).prefetch_related(
                Prefetch(
                    'items',
                    queryset=OrderItem.objects.select_related('product', 'product__seller')
                )
            ).filter(user=self.request.user).order_by('-created_at')
        return Order.objects.none()

class OrderDetailView(generics.RetrieveAPIView):
    """Retrieve a specific order with optimized queries"""
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        Order = apps.get_model('store', 'Order')
        OrderItem = apps.get_model('store', 'OrderItem')
        
        if self.request.user.is_authenticated:
            return Order.objects.select_related(
                'user'
            ).prefetch_related(
                Prefetch(
                    'items',
                    queryset=OrderItem.objects.select_related('product', 'product__seller')
                )
            ).filter(user=self.request.user)
        return Order.objects.none()

class UserProfileView(APIView):
    """Manage user profile"""
    def get(self, request):
        if request.user.is_authenticated:
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data)
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    
    def put(self, request):
        if request.user.is_authenticated:
            # Update user profile
            return Response({'message': 'Profile updated'}, status=status.HTTP_200_OK)
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

class DashboardStatisticsView(APIView):
    """Get dashboard statistics for authenticated users"""
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Import models
        Product = apps.get_model('store', 'Product')
        Order = apps.get_model('store', 'Order')
        UserProfile = apps.get_model('store', 'UserProfile')
        Commission = apps.get_model('store', 'Commission')
        OrderItem = apps.get_model('store', 'OrderItem')
        
        # Get statistics with optimized queries
        if request.user.is_staff:
            # Admin statistics
            total_products = Product.objects.count()
            total_orders = Order.objects.count()
            pending_orders = Order.objects.filter(status='pending').count()
            total_sellers = UserProfile.objects.filter(role='seller').count()
            total_profits = Commission.objects.aggregate(total=Sum('amount'))['total'] or 0
            pending_products = Product.objects.filter(verification_status='pending').count()
            rejected_products = Product.objects.filter(verification_status='rejected').count()
            
            # Recent orders
            recent_orders = Order.objects.select_related(
                'user'
            ).prefetch_related(
                Prefetch(
                    'items',
                    queryset=OrderItem.objects.select_related('product', 'product__seller')
                )
            ).order_by('-created_at')[:10]
            
            data = {
                'total_products': total_products,
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'total_sellers': total_sellers,
                'total_profits': float(total_profits),
                'pending_products': pending_products,
                'rejected_products': rejected_products,
                'recent_orders_count': recent_orders.count(),
            }
        else:
            # Regular user statistics
            user_orders = Order.objects.filter(user=request.user)
            total_orders = user_orders.count()
            pending_orders = user_orders.filter(status='pending').count()
            
            data = {
                'total_orders': total_orders,
                'pending_orders': pending_orders,
            }
        
        return Response(data)

class UserSearchView(APIView):
    """Search users (admin only)"""
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        # Import models
        User = apps.get_model('auth', 'User')
        UserProfile = apps.get_model('store', 'UserProfile')
        Order = apps.get_model('store', 'Order')
        
        # Get search query
        query = request.query_params.get('q', '')
        
        # Search users with optimized queries
        users = User.objects.select_related(
            'userprofile'
        ).prefetch_related(
            Prefetch(
                'order_set',
                queryset=Order.objects.only('id', 'status', 'total_amount')
            )
        )
        
        if query:
            users = users.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )
        
        # Serialize results (simplified)
        user_data = []
        for user in users[:20]:  # Limit to 20 results
            user_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': getattr(user.userprofile, 'role', 'buyer') if hasattr(user, 'userprofile') else 'buyer',
                'order_count': user.order_set.count(),
            })
        
        return Response({
            'users': user_data,
            'count': len(user_data)
        })