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
    
    # User API endpoints
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Review API endpoints
    path('reviews/', views.ReviewListView.as_view(), name='review_list'),
    path('reviews/<int:pk>/', views.ReviewDetailView.as_view(), name='review_detail'),
    
    # Coupon API endpoints
    path('coupons/', views.CouponListView.as_view(), name='coupon_list'),
    path('coupons/<int:pk>/', views.CouponDetailView.as_view(), name='coupon_detail'),
    
    # Loyalty Program API endpoints
    path('loyalty-programs/', views.LoyaltyProgramListView.as_view(), name='loyalty_program_list'),
    path('loyalty-programs/<int:pk>/', views.LoyaltyProgramDetailView.as_view(), name='loyalty_program_detail'),
    
    # Notification API endpoints
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    
    # Wishlist API endpoints
    path('wishlists/', views.WishlistListView.as_view(), name='wishlist_list'),
    
    # Page API endpoints
    path('pages/', views.PageListView.as_view(), name='page_list'),
    path('pages/<int:pk>/', views.PageDetailView.as_view(), name='page_detail'),
    
    # Article API endpoints
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    
    # FAQ API endpoints
    path('faqs/', views.FAQListView.as_view(), name='faq_list'),
    
    # Commission API endpoints
    path('commissions/', views.CommissionListView.as_view(), name='commission_list'),
    
    # Analytics API endpoints
    path('analytics/events/', views.AnalyticsEventCreateView.as_view(), name='analytics_event_create'),
    path('analytics/dashboard/', views.DashboardAnalyticsView.as_view(), name='dashboard_analytics'),
]