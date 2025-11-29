from rest_framework import serializers
from .models import Order, OrderItem, ShippingAddress, Payment, OrderTracking
import uuid

class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product_name', 'product_price', 'quantity', 'total_price']

class OrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTracking
        fields = ['id', 'status', 'location', 'notes', 'timestamp']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    tracking_history = OrderTrackingSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'total_amount', 'status', 'status_display', 
            'payment_method', 'payment_method_display', 'payment_status',
            'shipping_address', 'phone_number', 'created_at', 'updated_at',
            'shipped_at', 'delivered_at', 'items', 'tracking_history'
        ]

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = [
            'user', 'total_amount', 'payment_method', 'shipping_address', 
            'phone_number', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        # Create initial tracking entry
        OrderTracking.objects.create(
            order=order,
            status=order.status,
            notes="Order created"
        )
        
        return order

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = [
            'id', 'user', 'full_name', 'address_line_1', 'address_line_2',
            'city', 'state', 'postal_code', 'country', 'phone_number', 
            'is_default', 'created_at'
        ]

class PaymentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'payment_method', 'payment_method_display',
            'amount', 'transaction_id', 'status', 'status_display', 
            'payment_date'
        ]