from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment Methods
    path('methods/', views.PaymentMethodListView.as_view(), name='payment_method_list'),
    path('methods/<int:pk>/', views.PaymentMethodDetailView.as_view(), name='payment_method_detail'),
    
    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/<uuid:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    
    # Payment Processing
    path('process/', views.process_payment, name='process_payment'),
    
    # Refunds
    path('refunds/', views.RefundListView.as_view(), name='refund_list'),
    path('transactions/<uuid:transaction_id>/refund/', views.request_refund, name='request_refund'),
    
    # Payouts
    path('payouts/', views.PayoutListView.as_view(), name='payout_list'),
]