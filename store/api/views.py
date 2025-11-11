from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.apps import apps
from django.shortcuts import get_object_or_404
from decimal import Decimal
import stripe
import paypalrestsdk
from django.conf import settings

# Import models dynamically
Product = apps.get_model('store', 'Product')
Order = apps.get_model('store', 'Order')
OrderItem = apps.get_model('store', 'OrderItem')
Payment = apps.get_model('store', 'Payment')

class ProductListView(generics.ListAPIView):
    """List all products"""
    serializer_class = None  # Will be implemented with proper serializer
    
    def get_queryset(self):
        return Product.objects.all()

class ProductDetailView(generics.RetrieveAPIView):
    """Retrieve a specific product"""
    serializer_class = None  # Will be implemented with proper serializer
    
    def get_queryset(self):
        return Product.objects.all()

class OrderListView(generics.ListAPIView):
    """List all orders for the authenticated user"""
    serializer_class = None  # Will be implemented with proper serializer
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderDetailView(generics.RetrieveAPIView):
    """Retrieve a specific order"""
    serializer_class = None  # Will be implemented with proper serializer
    
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