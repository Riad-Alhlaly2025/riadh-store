from django.urls import path, include
from . import views
from . import views_security
from . import views_cms
from . import views_support

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/create-order/', views.create_order, name='create_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/', views.order_history, name='order_history'),
    path('notifications/', views.notifications, name='notifications'),
    path('notification/<int:notification_id>/read/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('optimize-images/', views.optimize_images_view, name='optimize_images'),
    path('signup/', views.signup, name='signup'),
    
    # Dashboard URLs
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('buyer/dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
    
    # Seller URLs
    path('seller/products/', views.seller_products, name='seller_products'),
    path('seller/products/add/', views.add_product, name='add_product'),
    path('seller/products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('seller/products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('seller/orders/', views.seller_orders, name='seller_orders'),
    path('seller/orders/<int:order_id>/', views.seller_order_detail, name='seller_order_detail'),
    path('seller/orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('seller/reports/', views.seller_reports, name='seller_reports'),
    path('seller/inventory/', views.inventory_management, name='inventory_management'),
    path('manager/reports/smart-inventory/', views.smart_inventory_reports, name='smart_inventory_reports'),
    path('manager/reports/seller-performance/', views.seller_performance_analytics, name='seller_performance_analytics'),
    
    # Commissions URLs
    path('commissions/', views.view_commissions, name='view_commissions'),
    path('commission/<int:commission_id>/pay/', views.pay_commission, name='pay_commission'),
    path('manager/commission-report/', views.commission_report, name='commission_report'),
    
    # Advanced Features URLs
    path('manager/sellers/', views.manage_sellers, name='manage_sellers'),
    path('order/<int:order_id>/dispute/', views.open_dispute, name='open_dispute'),
    path('manager/disputes/', views.manage_disputes, name='manage_disputes'),
    path('manager/reports/advanced/', views.advanced_reports, name='advanced_reports'),
    path('manager/reports/ai-analytics/', views.ai_analytics_dashboard, name='ai_analytics_dashboard'),
    path('manager/reports/financial/', views.financial_reports, name='financial_reports'),
    
    # Wishlist URLs
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Review URLs
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    
    # Product Comparison URLs
    path('comparison/', views.view_comparison, name='view_comparison'),
    path('comparison/add/<int:product_id>/', views.add_to_comparison, name='add_to_comparison'),
    path('comparison/remove/<int:product_id>/', views.remove_from_comparison, name='remove_from_comparison'),
    
    # Advanced Search URLs
    path('search/advanced/', views.advanced_search, name='advanced_search'),
    
    # Payment URLs
    path('payment/<int:order_id>/', views.payment_view, name='payment_view'),
    path('payment/create-payment-intent/<int:order_id>/', views.create_stripe_payment_intent, name='create_payment_intent'),
    path('payment/create-paypal-payment/<int:order_id>/', views.create_paypal_payment, name='create_paypal_payment'),
    path('payment/execute-paypal-payment/<int:payment_id>/', views.execute_paypal_payment, name='execute_paypal_payment'),
    path('payment/webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('payment/apple-pay/<int:order_id>/', views.create_apple_pay_payment, name='create_apple_pay_payment'),
    path('payment/google-pay/<int:order_id>/', views.create_google_pay_payment, name='create_google_pay_payment'),
    path('payment/cash-on-delivery/<int:order_id>/', views.cash_on_delivery_payment, name='cash_on_delivery_payment'),
    
    # New URLs for missing features
    # Coupon URLs
    path('coupon/apply/', views.apply_coupon, name='apply_coupon'),
    path('coupon/remove/', views.remove_coupon, name='remove_coupon'),
    path('manager/coupons/', views.coupon_management, name='coupon_management'),
    path('manager/coupons/delete/<int:coupon_id>/', views.delete_coupon, name='delete_coupon'),
    
    # Loyalty Program URLs
    path('loyalty/', views.loyalty_dashboard, name='loyalty_dashboard'),
    path('loyalty/redeem/<int:reward_id>/', views.redeem_reward, name='redeem_reward'),
    path('manager/loyalty-program/', views.loyalty_program_management, name='loyalty_program_management'),
    path('manager/loyalty-program/delete/<int:reward_id>/', views.delete_loyalty_reward, name='delete_loyalty_reward'),
    
    # Email Marketing URLs
    path('manager/email-campaigns/', views.email_campaigns, name='email_campaigns'),
    path('manager/email-campaigns/send/<int:campaign_id>/', views.send_email_campaign, name='send_email_campaign'),
    path('manager/email-campaigns/delete/<int:campaign_id>/', views.delete_email_campaign, name='delete_email_campaign'),
    
    # Recommendation URLs
    path('recommendations/', views.get_recommendations, name='recommendations'),
    path('track-behavior/', views.track_user_behavior, name='track_behavior'),
    
    # Advertising Campaign URLs
    path('manager/advertising-campaigns/', views.advertising_campaigns, name='advertising_campaigns'),
    path('manager/advertising-campaigns/delete/<int:campaign_id>/', views.delete_advertising_campaign, name='delete_advertising_campaign'),
    
    # New URLs for integration features
    # Social Media Integration URLs
    path('manager/social-media/', views.social_media_integration, name='social_media_integration'),
    path('manager/social-media/delete/<int:integration_id>/', views.delete_social_media_integration, name='delete_social_media_integration'),
    
    # Shipping Integration URLs
    path('manager/shipping/', views.shipping_integration, name='shipping_integration'),
    path('manager/shipping/delete/<int:integration_id>/', views.delete_shipping_integration, name='delete_shipping_integration'),
    
    # External Inventory URLs
    path('manager/inventory/external/', views.external_inventory, name='external_inventory'),
    path('manager/inventory/external/delete/<int:inventory_id>/', views.delete_external_inventory, name='delete_external_inventory'),
    
    # Accounting Integration URLs
    path('manager/accounting/', views.accounting_integration, name='accounting_integration'),
    path('manager/accounting/delete/<int:integration_id>/', views.delete_accounting_integration, name='delete_accounting_integration'),
    
    # Analytics Integration URLs
    path('manager/analytics/', views.analytics_integration, name='analytics_integration'),
    path('track-analytics/', views.track_analytics_event, name='track_analytics'),
    path('export-analytics/<str:format>/', views.export_analytics_report, name='export_analytics_report'),
    
    # New URLs for security features
    # MFA URLs
    path('security/mfa/setup/', views_security.mfa_setup, name='mfa_setup'),
    path('security/mfa/verify/', views_security.mfa_verify, name='mfa_verify'),
    path('security/mfa/devices/', views_security.mfa_device_list, name='mfa_device_list'),
    path('security/mfa/device/<int:device_id>/delete/', views_security.mfa_delete_device, name='mfa_delete_device'),
    
    # Security Log URLs
    path('security/logs/', views_security.security_logs, name='security_logs'),
    
    # Sensitive Data URLs
    path('security/sensitive-data/', views_security.sensitive_data_list, name='sensitive_data_list'),
    path('security/sensitive-data/add/', views_security.add_sensitive_data, name='add_sensitive_data'),
    path('security/sensitive-data/<int:data_id>/', views_security.view_sensitive_data, name='view_sensitive_data'),
    path('security/sensitive-data/<int:data_id>/delete/', views_security.delete_sensitive_data, name='delete_sensitive_data'),
    
    # CMS URLs
    # Page URLs
    path('pages/<slug:slug>/', views_cms.page_detail, name='page_detail'),
    path('manager/pages/', views_cms.page_list, name='page_list'),
    path('manager/pages/create/', views_cms.page_create, name='page_create'),
    path('manager/pages/<slug:slug>/edit/', views_cms.page_edit, name='page_edit'),
    path('manager/pages/<slug:slug>/delete/', views_cms.page_delete, name='page_delete'),
    
    # Article URLs
    path('articles/', views_cms.article_list, name='article_list'),
    path('articles/<slug:slug>/', views_cms.article_detail, name='article_detail'),
    path('manager/articles/', views_cms.article_list_manager, name='article_list_manager'),
    path('manager/articles/create/', views_cms.article_create, name='article_create'),
    path('manager/articles/<slug:slug>/edit/', views_cms.article_edit, name='article_edit'),
    path('manager/articles/<slug:slug>/delete/', views_cms.article_delete, name='article_delete'),
    
    # Landing Page URLs
    path('landing/<slug:slug>/', views_cms.landing_page_detail, name='landing_page_detail'),
    path('manager/landing-pages/', views_cms.landing_page_list, name='landing_page_list'),
    path('manager/landing-pages/create/', views_cms.landing_page_create, name='landing_page_create'),
    path('manager/landing-pages/<slug:slug>/edit/', views_cms.landing_page_edit, name='landing_page_edit'),
    path('manager/landing-pages/<slug:slug>/delete/', views_cms.landing_page_delete, name='landing_page_delete'),
    
    # Comment URLs
    path('manager/comments/', views_cms.comment_list, name='comment_list'),
    path('manager/comments/<int:comment_id>/update-status/', views_cms.comment_update_status, name='comment_update_status'),
    path('manager/comments/<int:comment_id>/delete/', views_cms.comment_delete, name='comment_delete'),
    
    # Customer Support URLs
    # Live Chat URLs
    path('support/chat/', views_support.chat_list, name='chat_list'),
    path('support/chat/<int:chat_id>/', views_support.chat_detail, name='chat_detail'),
    path('support/chat/start/', views_support.start_chat, name='start_chat'),
    path('support/chat/agent/', views_support.agent_chat_list, name='agent_chat_list'),
    path('support/chat/<int:chat_id>/assign/', views_support.assign_chat, name='assign_chat'),
    path('support/chat/<int:chat_id>/close/', views_support.close_chat, name='close_chat'),
    
    # Support Ticket URLs
    path('support/tickets/', views_support.ticket_list, name='ticket_list'),
    path('support/tickets/<int:ticket_id>/', views_support.ticket_detail, name='ticket_detail'),
    path('support/tickets/create/', views_support.create_ticket, name='create_ticket'),
    path('support/tickets/agent/', views_support.agent_ticket_list, name='agent_ticket_list'),
    path('support/tickets/<int:ticket_id>/assign/', views_support.assign_ticket, name='assign_ticket'),
    path('support/tickets/<int:ticket_id>/resolve/', views_support.resolve_ticket, name='resolve_ticket'),
    
    # FAQ URLs
    path('support/faq/', views_support.faq_list, name='faq_list'),
    path('support/faq/<int:faq_id>/', views_support.faq_detail, name='faq_detail'),
    path('manager/faq/categories/', views_support.faq_category_list, name='faq_category_list'),
    path('manager/faq/categories/create/', views_support.faq_category_create, name='faq_category_create'),
    path('manager/faq/categories/<int:category_id>/edit/', views_support.faq_category_edit, name='faq_category_edit'),
    path('manager/faq/categories/<int:category_id>/delete/', views_support.faq_category_delete, name='faq_category_delete'),
    path('manager/faq/', views_support.faq_list_manager, name='faq_list_manager'),
    path('manager/faq/create/', views_support.faq_create, name='faq_create'),
    path('manager/faq/<int:faq_id>/edit/', views_support.faq_edit, name='faq_edit'),
    path('manager/faq/<int:faq_id>/delete/', views_support.faq_delete, name='faq_delete'),
    
    # Enhanced Review URLs
    path('product/<int:product_id>/reviews/', views_support.product_reviews, name='product_reviews'),
    path('product/<int:product_id>/review/add/', views_support.add_review, name='add_enhanced_review'),
    path('review/<int:review_id>/<str:action>/', views_support.review_helpfulness, name='review_helpfulness'),
    path('manager/reviews/', views_support.review_list_manager, name='review_list_manager'),
    path('manager/review/<int:review_id>/toggle-featured/', views_support.toggle_featured_review, name='toggle_featured_review'),
    
    # Debug URL
    path('debug/manager-access/', views.debug_manager_access, name='debug_manager_access'),

    # API URLs
    path('api/', include('store.api.urls')),
]