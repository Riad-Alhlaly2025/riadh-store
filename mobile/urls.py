from django.urls import path
from . import api

app_name = 'mobile_api'

urlpatterns = [
    path('home/', api.mobile_home_data, name='home_data'),
    path('products/', api.mobile_product_list, name='product_list'),
    path('products/<int:product_id>/', api.mobile_product_detail, name='product_detail'),
    path('cart/', api.mobile_cart, name='cart'),
    path('profile/', api.mobile_user_profile, name='user_profile'),
    path('dashboard/', api.mobile_user_dashboard, name='user_dashboard'),
    path('orders/', api.mobile_user_orders, name='user_orders'),
]