from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.apps import apps
from django.shortcuts import get_object_or_404
from .serializers import (
    ProductSerializer, 
    CategorySerializer, 
    CartSerializer, 
    OrderSerializer, 
    UserProfileSerializer
)

class ProductListView(generics.ListAPIView):
    """List all products"""
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        Product = apps.get_model('store', 'Product')
        return Product.objects.all()

class ProductDetailView(generics.RetrieveAPIView):
    """Retrieve a specific product"""
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        Product = apps.get_model('store', 'Product')
        return Product.objects.all()

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
    """List user orders"""
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        Order = apps.get_model('store', 'Order')
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.none()

class OrderDetailView(generics.RetrieveAPIView):
    """Retrieve a specific order"""
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        Order = apps.get_model('store', 'Order')
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
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