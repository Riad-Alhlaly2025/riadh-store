from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'store_api'

urlpatterns = [
    # Product API endpoints
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Order API endpoints
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    
    # Payment API endpoints
    path('payments/stripe/', views.StripePaymentView.as_view(), name='stripe_payment'),
    path('payments/paypal/create/', views.PayPalCreatePaymentView.as_view(), name='paypal_create'),
    path('payments/paypal/execute/', views.PayPalExecutePaymentView.as_view(), name='paypal_execute'),
]