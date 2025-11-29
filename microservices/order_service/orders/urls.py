from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order_list'),
    path('<uuid:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('create/', views.create_order, name='create_order'),
    path('history/', views.order_history, name='order_history'),
    path('<uuid:order_id>/status/', views.update_order_status, name='update_order_status'),
    path('<uuid:order_id>/tracking/', views.order_tracking, name='order_tracking'),
    
    # Shipping Address URLs
    path('shipping-addresses/', views.ShippingAddressListView.as_view(), name='shipping_address_list'),
    path('shipping-addresses/<int:pk>/', views.ShippingAddressDetailView.as_view(), name='shipping_address_detail'),
    path('shipping-addresses/<int:address_id>/set-default/', views.set_default_shipping_address, name='set_default_shipping_address'),
    
    # Payment URLs
    path('<uuid:order_id>/payment/', views.process_payment, name='process_payment'),
    
    # Summary
    path('summary/', views.order_summary, name='order_summary'),
]