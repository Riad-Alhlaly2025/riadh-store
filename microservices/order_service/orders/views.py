from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Order, OrderItem, ShippingAddress, Payment, OrderTracking
from .serializers import OrderSerializer, OrderCreateSerializer, ShippingAddressSerializer, PaymentSerializer

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Create a new order"""
    serializer = OrderCreateSerializer(data=request.data)
    if serializer.is_valid():
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_history(request):
    """Get user's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """Update order status (for admin use)"""
    order = get_object_or_404(Order, id=order_id)
    
    # Check if user is admin or owner of the order
    if not request.user.is_staff and order.user != request.user:
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    new_status = request.data.get('status')
    if not new_status:
        return Response(
            {'error': 'Status is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate status
    valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return Response(
            {'error': f'Invalid status. Valid options: {valid_statuses}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update order status
    old_status = order.status
    order.status = new_status
    order.save()
    
    # Create tracking entry
    OrderTracking.objects.create(
        order=order,
        status=new_status,
        notes=f"Status updated from {old_status} to {new_status}"
    )
    
    serializer = OrderSerializer(order)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_tracking(request, order_id):
    """Get order tracking information"""
    order = get_object_or_404(Order, id=order_id)
    
    # Check if user is admin or owner of the order
    if not request.user.is_staff and order.user != request.user:
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    tracking_history = OrderTracking.objects.filter(order=order).order_by('timestamp')
    serializer = OrderTrackingSerializer(tracking_history, many=True)
    return Response(serializer.data)

# Shipping Address Views
class ShippingAddressListView(generics.ListCreateAPIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ShippingAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_default_shipping_address(request, address_id):
    """Set a shipping address as default"""
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    
    # Set all other addresses as non-default
    ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # Set this address as default
    address.is_default = True
    address.save()
    
    return Response({'message': 'Default shipping address updated'})

# Payment Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_payment(request, order_id):
    """Process payment for an order"""
    order = get_object_or_404(Order, id=order_id)
    
    # Check if user is admin or owner of the order
    if not request.user.is_staff and order.user != request.user:
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    payment_data = request.data
    payment_data['order'] = order_id
    
    serializer = PaymentSerializer(data=payment_data)
    if serializer.is_valid():
        payment = serializer.save()
        
        # Update order payment status
        order.payment_status = payment.status
        order.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_summary(request):
    """Get order summary statistics for the user"""
    user_orders = Order.objects.filter(user=request.user)
    
    total_orders = user_orders.count()
    pending_orders = user_orders.filter(status='pending').count()
    processing_orders = user_orders.filter(status='processing').count()
    shipped_orders = user_orders.filter(status='shipped').count()
    delivered_orders = user_orders.filter(status='delivered').count()
    cancelled_orders = user_orders.filter(status='cancelled').count()
    
    # Calculate total spent
    total_spent = sum(order.total_amount for order in user_orders.filter(status='delivered'))
    
    summary = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
        'total_spent': float(total_spent),
    }
    
    return Response(summary)