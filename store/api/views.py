from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.apps import apps
from django.shortcuts import get_object_or_404
from decimal import Decimal
import stripe
import paypalrestsdk
from django.conf import settings
from django.db.models import Sum, Count
from .serializers import ProductSerializer, OrderSerializer, PaymentSerializer, UserSerializer, ReviewSerializer, CouponSerializer, LoyaltyProgramSerializer, NotificationSerializer, WishlistSerializer, PageSerializer, ArticleSerializer, LandingPageSerializer, CommentSerializer, LiveChatSessionSerializer, SupportTicketSerializer, FAQSerializer, CommissionSerializer, ShippingCompanySerializer, TaxRateSerializer, MFADeviceSerializer, SecurityLogSerializer, SensitiveDataSerializer, AnalyticsIntegrationSerializer

# Import models dynamically
Product = apps.get_model('store', 'Product')
Order = apps.get_model('store', 'Order')
OrderItem = apps.get_model('store', 'OrderItem')
Payment = apps.get_model('store', 'Payment')
User = apps.get_model('auth', 'User')
Review = apps.get_model('store', 'Review')
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
Commission = apps.get_model('store', 'Commission')
ShippingCompany = apps.get_model('store', 'ShippingCompany')
TaxRate = apps.get_model('store', 'TaxRate')
MFADevice = apps.get_model('store', 'MFADevice')
SecurityLog = apps.get_model('store', 'SecurityLog')
SensitiveData = apps.get_model('store', 'SensitiveData')
AnalyticsIntegration = apps.get_model('store', 'AnalyticsIntegration')

class ProductListView(generics.ListAPIView):
    """List all products"""
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Product.objects.all()

class ProductDetailView(generics.RetrieveAPIView):
    """Retrieve a specific product"""
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Product.objects.all()

class OrderListView(generics.ListAPIView):
    """List all orders for the authenticated user"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderDetailView(generics.RetrieveAPIView):
    """Retrieve a specific order"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class StripePaymentView(APIView):
    """Process Stripe payment"""
    
    def post(self, request):
        try:
            # Get order ID and payment method from request
            order_id = request.data.get('order_id')
            order = get_object_or_404(Order, id=order_id, user=request.user)
            
            # Create Stripe payment intent
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),  # Convert to cents
                currency=order.items.first().product.currency.lower() if order.items.exists() else 'usd',
                metadata={
                    'order_id': order_id,
                }
            )
            
            # Create payment record
            payment = Payment.objects.create(
                order=order,
                payment_method='stripe',
                transaction_id=intent.id,
                amount=order.total_amount,
                currency=order.items.first().product.currency if order.items.exists() else 'USD',
                status='pending'
            )
            
            return Response({
                'client_secret': intent.client_secret,
                'payment_id': payment.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class PayPalCreatePaymentView(APIView):
    """Create PayPal payment"""
    
    def post(self, request):
        try:
            # Get order ID from request
            order_id = request.data.get('order_id')
            order = get_object_or_404(Order, id=order_id, user=request.user)
            
            # Configure PayPal
            paypalrestsdk.configure({
                'mode': settings.PAYPAL_MODE,
                'client_id': settings.PAYPAL_CLIENT_ID,
                'client_secret': settings.PAYPAL_CLIENT_SECRET
            })
            
            # Create PayPal payment
            payment = paypalrestsdk.Payment({
                'intent': 'sale',
                'payer': {
                    'payment_method': 'paypal'
                },
                'transactions': [{
                    'amount': {
                        'total': str(order.total_amount),
                        'currency': order.items.first().product.currency if order.items.exists() else 'USD'
                    },
                    'description': f'Payment for order #{order_id}'
                }],
                'redirect_urls': {
                    'return_url': request.build_absolute_uri('/payment/paypal/execute/'),
                    'cancel_url': request.build_absolute_uri('/payment/paypal/cancel/')
                }
            })
            
            if payment.create():
                # Create payment record
                payment_record = Payment.objects.create(
                    order=order,
                    payment_method='paypal',
                    transaction_id=payment.id,
                    amount=order.total_amount,
                    currency=order.items.first().product.currency if order.items.exists() else 'USD',
                    status='pending'
                )
                
                # Find approval URL
                approval_url = None
                for link in payment.links:
                    if link.rel == 'approval_url':
                        approval_url = link.href
                        break
                
                return Response({
                    'payment_id': payment_record.id,
                    'approval_url': approval_url
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': payment.error
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class PayPalExecutePaymentView(APIView):
    """Execute PayPal payment"""
    
    def post(self, request):
        try:
            # Get payment ID and Payer ID from request
            payment_id = request.data.get('payment_id')
            payer_id = request.data.get('payer_id')
            
            # Configure PayPal
            paypalrestsdk.configure({
                'mode': settings.PAYPAL_MODE,
                'client_id': settings.PAYPAL_CLIENT_ID,
                'client_secret': settings.PAYPAL_CLIENT_SECRET
            })
            
            # Get payment
            payment = paypalrestsdk.Payment.find(payment_id)
            
            # Execute payment
            if payment.execute({'payer_id': payer_id}):
                # Update payment record
                payment_record = Payment.objects.get(transaction_id=payment_id)
                payment_record.status = 'completed'
                payment_record.save()
                
                # Update order status
                order = payment_record.order
                order.status = 'processing'
                order.save()
                
                return Response({
                    'message': 'Payment executed successfully',
                    'order_id': order.id
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': payment.error
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class AnalyticsEventCreateView(APIView):
    """Create an analytics event"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            event_type = request.data.get('event_type')
            product_id = request.data.get('product_id')
            order_id = request.data.get('order_id')
            metadata = request.data.get('metadata', '')
            
            # Create analytics event
            event = AnalyticsIntegration.objects.create(
                user=request.user,
                event_type=event_type,
                url=request.data.get('url', ''),
                referrer=request.data.get('referrer', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=request.META.get('REMOTE_ADDR', ''),
                metadata=metadata
            )
            
            # Associate with product if provided
            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                    event.product = product
                    event.save()
                except Product.DoesNotExist:
                    pass
            
            # Associate with order if provided
            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                    event.order = order
                    event.save()
                except Order.DoesNotExist:
                    pass
            
            return Response({
                'message': 'Analytics event tracked successfully',
                'event_id': event.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    """List all users (admin only)"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only managers can see all users
        if hasattr(self.request.user, 'userprofile') and self.request.user.userprofile.role == 'manager':
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)


class UserDetailView(generics.RetrieveAPIView):
    """Retrieve a specific user"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own profile, managers can see all
        if hasattr(self.request.user, 'userprofile') and self.request.user.userprofile.role == 'manager':
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)


class ReviewListView(generics.ListAPIView):
    """List all reviews"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.all()


class ReviewDetailView(generics.RetrieveAPIView):
    """Retrieve a specific review"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.all()


class CouponListView(generics.ListAPIView):
    """List all coupons (manager only)"""
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only managers can see all coupons
        if hasattr(self.request.user, 'userprofile') and self.request.user.userprofile.role == 'manager':
            return Coupon.objects.all()
        return Coupon.objects.none()


class CouponDetailView(generics.RetrieveAPIView):
    """Retrieve a specific coupon (manager only)"""
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only managers can see coupons
        if hasattr(self.request.user, 'userprofile') and self.request.user.userprofile.role == 'manager':
            return Coupon.objects.all()
        return Coupon.objects.none()


class LoyaltyProgramListView(generics.ListAPIView):
    """List all loyalty programs (manager only)"""
    serializer_class = LoyaltyProgramSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only managers can see all loyalty programs
        if hasattr(self.request.user, 'userprofile') and self.request.user.userprofile.role == 'manager':
            return LoyaltyProgram.objects.all()
        return LoyaltyProgram.objects.filter(user=self.request.user)


class LoyaltyProgramDetailView(generics.RetrieveAPIView):
    """Retrieve a specific loyalty program"""
    serializer_class = LoyaltyProgramSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own loyalty program, managers can see all
        if hasattr(self.request.user, 'userprofile') and self.request.user.userprofile.role == 'manager':
            return LoyaltyProgram.objects.all()
        return LoyaltyProgram.objects.filter(user=self.request.user)


class NotificationListView(generics.ListAPIView):
    """List all notifications for the authenticated user"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationDetailView(generics.RetrieveAPIView):
    """Retrieve a specific notification"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class WishlistListView(generics.ListAPIView):
    """List all wishlist items for the authenticated user"""
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


class PageListView(generics.ListAPIView):
    """List all published pages"""
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Page.objects.filter(status='published')


class PageDetailView(generics.RetrieveAPIView):
    """Retrieve a specific page"""
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Page.objects.filter(status='published')


class ArticleListView(generics.ListAPIView):
    """List all published articles"""
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Article.objects.filter(status='published')


class ArticleDetailView(generics.RetrieveAPIView):
    """Retrieve a specific article"""
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Article.objects.filter(status='published')


class FAQListView(generics.ListAPIView):
    """List all active FAQs"""
    serializer_class = FAQSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FAQ.objects.filter(is_active=True)


class CommissionListView(generics.ListAPIView):
    """List all commissions for the authenticated user"""
    serializer_class = CommissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own commissions, managers can see all
        if hasattr(self.request.user, 'userprofile') and self.request.user.userprofile.role == 'manager':
            return Commission.objects.all()
        return Commission.objects.filter(user=self.request.user)


class DashboardAnalyticsView(APIView):
    """Get dashboard analytics data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get basic statistics
            total_products = Product.objects.count()
            total_orders = Order.objects.count()
            total_users = User.objects.count()
            total_revenue = Order.objects.filter(status='delivered').aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            # User statistics
            sellers_count = User.objects.filter(userprofile__role='seller').count()
            buyers_count = User.objects.filter(userprofile__role='buyer').count()
            managers_count = User.objects.filter(userprofile__role='manager').count()
            
            # Recent orders
            recent_orders = Order.objects.all().order_by('-created_at')[:5]
            recent_orders_data = []
            for order in recent_orders:
                recent_orders_data.append({
                    'id': order.id,
                    'user': order.user.username if order.user else 'Unknown',
                    'total_amount': str(order.total_amount),
                    'status': order.status,
                    'created_at': order.created_at.isoformat()
                })
            
            return Response({
                'statistics': {
                    'total_products': total_products,
                    'total_orders': total_orders,
                    'total_users': total_users,
                    'total_revenue': str(total_revenue),
                    'sellers_count': sellers_count,
                    'buyers_count': buyers_count,
                    'managers_count': managers_count
                },
                'recent_orders': recent_orders_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
