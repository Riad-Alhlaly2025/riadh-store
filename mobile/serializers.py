from rest_framework import serializers
from django.contrib.auth.models import User
from django.apps import apps

class MobileProductSerializer(serializers.Serializer):
    """Serializer for product data in mobile API"""
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    category = serializers.CharField(max_length=100)
    image = serializers.ImageField()
    seller_name = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    def get_seller_name(self, obj):
        return obj.seller.username if obj.seller else "Unknown"
    
    def get_rating(self, obj):
        # Return average rating if you have a review system
        return 4.5  # Placeholder
    
    def get_review_count(self, obj):
        # Return number of reviews if you have a review system
        return 12  # Placeholder

class MobileCategorySerializer(serializers.Serializer):
    """Serializer for category data in mobile API"""
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    product_count = serializers.SerializerMethodField()
    
    def get_product_count(self, obj):
        Product = apps.get_model('store', 'Product')
        return Product.objects.filter(category=obj.name).count()

class MobileCartItemSerializer(serializers.Serializer):
    """Serializer for cart item data in mobile API"""
    product = MobileProductSerializer()
    quantity = serializers.IntegerField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)

class MobileCartSerializer(serializers.Serializer):
    """Serializer for cart data in mobile API"""
    items = MobileCartItemSerializer(many=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    item_count = serializers.IntegerField()

class MobileOrderItemSerializer(serializers.Serializer):
    """Serializer for order item data in mobile API"""
    product = MobileProductSerializer()
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

class MobileOrderSerializer(serializers.Serializer):
    """Serializer for order data in mobile API"""
    id = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField(max_length=20)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    items = MobileOrderItemSerializer(many=True)

class MobileUserSerializer(serializers.ModelSerializer):
    """Serializer for user data in mobile API"""
    full_name = serializers.SerializerMethodField()
    order_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'date_joined', 'order_count']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def get_order_count(self, obj):
        Order = apps.get_model('store', 'Order')
        return Order.objects.filter(user=obj).count()