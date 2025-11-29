from rest_framework import serializers
from .models import PaymentMethod, Transaction, Refund, Payout

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'method_type', 'is_default', 'card_number_last4', 
                  'card_expiry_month', 'card_expiry_year', 'card_brand', 
                  'paypal_email', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class TransactionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'order_id', 'amount', 'currency', 'status', 
                  'status_display', 'transaction_type', 'transaction_type_display',
                  'provider', 'provider_transaction_id', 'description', 'metadata',
                  'created_at', 'updated_at', 'completed_at']
        read_only_fields = ['created_at', 'updated_at', 'completed_at']

class RefundSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Refund
        fields = ['id', 'transaction', 'amount', 'reason', 'status', 
                  'status_display', 'provider_refund_id', 'created_at', 
                  'updated_at', 'completed_at']
        read_only_fields = ['created_at', 'updated_at', 'completed_at']

class PayoutSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payout
        fields = ['id', 'user', 'amount', 'currency', 'status', 'status_display',
                  'provider', 'provider_payout_id', 'destination', 'created_at', 
                  'updated_at', 'completed_at']
        read_only_fields = ['created_at', 'updated_at', 'completed_at']