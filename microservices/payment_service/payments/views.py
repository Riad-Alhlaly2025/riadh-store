from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from .models import PaymentMethod, Transaction, Refund, Payout
from .serializers import PaymentMethodSerializer, TransactionSerializer, RefundSerializer, PayoutSerializer

class PaymentMethodListView(generics.ListCreateAPIView):
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Ensure only one default payment method per user
        if serializer.validated_data.get('is_default'):
            PaymentMethod.objects.filter(user=self.request.user, is_default=True).update(is_default=False)
        serializer.save(user=self.request.user)

class PaymentMethodDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        # Ensure only one default payment method per user
        if serializer.validated_data.get('is_default', False):
            PaymentMethod.objects.filter(user=self.request.user, is_default=True).exclude(
                pk=self.get_object().pk).update(is_default=False)
        serializer.save()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_payment(request):
    """
    Process a payment for an order
    """
    try:
        order_id = request.data.get('order_id')
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'USD')
        payment_method_id = request.data.get('payment_method_id')
        provider = request.data.get('provider')
        
        if not all([order_id, amount, provider]):
            return Response(
                {'error': 'order_id, amount, and provider are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create transaction record
        transaction = Transaction.objects.create(
            user=request.user,
            order_id=order_id,
            amount=amount,
            currency=currency,
            provider=provider,
            status='pending'
        )
        
        # Here you would integrate with actual payment providers (Stripe, PayPal, etc.)
        # For now, we'll simulate a successful payment
        transaction.status = 'completed'
        transaction.completed_at = timezone.now()
        transaction.save()
        
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_refund(request, transaction_id):
    """
    Request a refund for a transaction
    """
    try:
        transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
        amount = request.data.get('amount', transaction.amount)
        reason = request.data.get('reason', '')
        
        # Check if transaction can be refunded
        if transaction.status != 'completed':
            return Response(
                {'error': 'Only completed transactions can be refunded'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create refund record
        refund = Refund.objects.create(
            transaction=transaction,
            amount=amount,
            reason=reason,
            status='pending'
        )
        
        # Here you would integrate with actual payment providers to process the refund
        # For now, we'll simulate a successful refund
        refund.status = 'completed'
        refund.completed_at = timezone.now()
        refund.save()
        
        # Update transaction status
        transaction.status = 'refunded'
        transaction.save()
        
        serializer = RefundSerializer(refund)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class RefundListView(generics.ListAPIView):
    serializer_class = RefundSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Refund.objects.filter(transaction__user=self.request.user)

class PayoutListView(generics.ListCreateAPIView):
    serializer_class = PayoutSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payout.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)