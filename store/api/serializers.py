from rest_framework import serializers
from django.apps import apps

# Get models dynamically
Product = apps.get_model('store', 'Product')
Order = apps.get_model('store', 'Order')
OrderItem = apps.get_model('store', 'OrderItem')
Payment = apps.get_model('store', 'Payment')
User = apps.get_model('auth', 'User')
UserProfile = apps.get_model('store', 'UserProfile')
Review = apps.get_model('store', 'Review')
Category = apps.get_model('store', 'Category')
Coupon = apps.get_model('store', 'Coupon')
LoyaltyProgram = apps.get_model('store', 'LoyaltyProgram')
Notification = apps.get_model('store', 'Notification')
Wishlist = apps.get_model('store', 'Wishlist')
Page = apps.get_model('store', 'Page')
Article = apps.get_model('store', 'Article')
LandingPage = apps.get_model('store', 'LandingPage')
Comment = apps.get_model('store', 'Comment')
LiveChatSession = apps.get_model('store', 'LiveChatSession')
SupportTicket = apps.get_model('store', 'SupportTicket')
FAQ = apps.get_model('store', 'FAQ')
FAQCategory = apps.get_model('store', 'FAQCategory')
Commission = apps.get_model('store', 'Commission')
ShippingCompany = apps.get_model('store', 'ShippingCompany')
TaxRate = apps.get_model('store', 'TaxRate')
MFADevice = apps.get_model('store', 'MFADevice')
SecurityLog = apps.get_model('store', 'SecurityLog')
SensitiveData = apps.get_model('store', 'SensitiveData')
AnalyticsIntegration = apps.get_model('store', 'AnalyticsIntegration')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'role', 'verification_status', 'business_name', 'phone_number', 'address']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    # category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'description', 'image', 'category', 
            'currency', 'seller', 'stock_quantity', 'low_stock_threshold',
            'seo_title', 'seo_description', 'seo_keywords',
            'name_en', 'description_en', 'seo_title_en', 
            'seo_description_en', 'seo_keywords_en', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'total_price']
        read_only_fields = ['id', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'created_at', 'updated_at', 'status', 
            'total_amount', 'shipping_address', 'phone_number',
            'shipping_company', 'shipping_cost', 'tracking_number',
            'tax_amount', 'items'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'payment_method', 'transaction_id', 
            'amount', 'currency', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'product', 'user', 'rating', 'comment', 
            'created_at', 'updated_at', 'is_verified_purchase'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'discount_type', 'discount_value', 
            'minimum_amount', 'active', 'valid_from', 'valid_to',
            'usage_limit', 'times_used', 'created_at'
        ]
        read_only_fields = ['id', 'times_used', 'created_at']


class LoyaltyProgramSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = LoyaltyProgram
        fields = [
            'id', 'user', 'points', 'level', 'total_spent', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    order = OrderSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'order', 'notification_type', 'message', 
            'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WishlistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'created_at']
        read_only_fields = ['id', 'created_at']


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'featured_image',
            'status', 'created_at', 'updated_at', 'published_at',
            'seo_title', 'seo_description', 'seo_keywords'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'featured_image',
            'author', 'status', 'article_type', 'created_at', 'updated_at', 
            'published_at', 'views', 'seo_title', 'seo_description', 'seo_keywords'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'views']


class LandingPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandingPage
        fields = [
            'id', 'name', 'slug', 'title', 'subtitle', 'content',
            'call_to_action', 'call_to_action_url', 'background_image',
            'status', 'campaign_name', 'created_at', 'updated_at',
            'starts_at', 'ends_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    article = ArticleSerializer(read_only=True)
    page = PageSerializer(read_only=True)
    parent = 'self'
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'article', 'page', 'parent',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LiveChatSessionSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    support_agent = UserSerializer(read_only=True)
    
    class Meta:
        model = LiveChatSession
        fields = [
            'id', 'customer', 'support_agent', 'status', 
            'created_at', 'updated_at', 'closed_at', 'topic'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'closed_at']


class SupportTicketSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    assigned_agent = UserSerializer(read_only=True)
    
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'customer', 'assigned_agent', 'subject', 'description',
            'priority', 'status', 'category', 'created_at', 'updated_at',
            'resolved_at', 'attachment'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'resolved_at']


class FAQCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQCategory
        fields = ['id', 'name', 'description', 'order', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class FAQSerializer(serializers.ModelSerializer):
    category = FAQCategorySerializer(read_only=True)
    
    class Meta:
        model = FAQ
        fields = [
            'id', 'category', 'question', 'answer', 'order', 
            'is_active', 'created_at', 'updated_at', 'views'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'views']


class CommissionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    order = OrderSerializer(read_only=True)
    
    class Meta:
        model = Commission
        fields = [
            'id', 'user', 'order', 'amount', 'rate', 
            'created_at', 'is_paid'
        ]
        read_only_fields = ['id', 'created_at']


class ShippingCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingCompany
        fields = [
            'id', 'name', 'base_cost', 'cost_per_kg', 
            'delivery_time', 'is_active'
        ]
        read_only_fields = ['id']


class TaxRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRate
        fields = [
            'id', 'name', 'tax_type', 'rate', 'country_code',
            'region', 'postal_code', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MFADeviceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = MFADevice
        fields = [
            'id', 'user', 'name', 'secret_key', 'device_type',
            'is_active', 'created_at', 'last_used'
        ]
        read_only_fields = ['id', 'created_at', 'last_used']


class SecurityLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = SecurityLog
        fields = [
            'id', 'user', 'event_type', 'ip_address', 'user_agent',
            'timestamp', 'details', 'is_suspicious'
        ]
        read_only_fields = ['id', 'timestamp']


class SensitiveDataSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = SensitiveData
        fields = [
            'id', 'user', 'data_type', 'encrypted_data',
            'encryption_method', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AnalyticsIntegrationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    order = OrderSerializer(read_only=True)
    
    class Meta:
        model = AnalyticsIntegration
        fields = [
            'id', 'user', 'session_key', 'event_type', 'product',
            'order', 'url', 'referrer', 'user_agent', 'ip_address',
            'timestamp', 'metadata'
        ]
        read_only_fields = ['id', 'timestamp']