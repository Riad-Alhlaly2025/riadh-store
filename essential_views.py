# Essential views.py file with required functions for dashboard access

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.apps import apps
from django.db.models import Sum, Count
import logging

logger = logging.getLogger(__name__)

def home(request):
    """Home page view"""
    return render(request, 'store/home.html')

def product_list(request):
    """Product list view"""
    Product = apps.get_model('store', 'Product')
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

def product_detail(request, pk):
    """Product detail view"""
    Product = apps.get_model('store', 'Product')
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

def view_cart(request):
    """View cart"""
    return render(request, 'store/cart.html')

def add_to_cart(request, product_id):
    """Add product to cart"""
    return redirect('view_cart')

def remove_from_cart(request, product_id):
    """Remove product from cart"""
    return redirect('view_cart')

def update_cart(request, product_id):
    """Update cart item"""
    return redirect('view_cart')

def checkout(request):
    """Checkout view"""
    return render(request, 'store/checkout.html')

def order_detail(request, order_id):
    """Order detail view"""
    return render(request, 'store/order_detail.html')

def order_history(request):
    """Order history view"""
    return render(request, 'store/order_history.html')

def notifications(request):
    """Notifications view"""
    return render(request, 'store/notifications.html')

def mark_notification_as_read(request, notification_id):
    """Mark notification as read"""
    return JsonResponse({'status': 'success'})

def optimize_images_view(request):
    """Optimize images view"""
    return render(request, 'store/optimize_images.html')

def signup(request):
    """Signup view"""
    return render(request, 'store/signup.html')

@login_required
def manager_dashboard(request):
    """Manager dashboard view"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى لوحة تحكم المدير')
        return redirect('home')
    
    # Import models
    Product = apps.get_model('store', 'Product')
    Order = apps.get_model('store', 'Order')
    
    # Get statistics
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
    }
    
    return render(request, 'store/manager_dashboard.html', context)

@login_required
def seller_dashboard(request):
    """Seller dashboard view"""
    # Check if user has seller profile
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'seller':
            messages.error(request, 'ليس لديك صلاحية الوصول إلى لوحة تحكم البائع')
            return redirect('home')
    except:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى لوحة تحكم البائع')
        return redirect('home')
    
    # Import models
    Product = apps.get_model('store', 'Product')
    Order = apps.get_model('store', 'Order')
    
    # Get seller-specific statistics
    seller_products = Product.objects.filter(seller=request.user)
    total_products = seller_products.count()
    
    # Get orders for seller's products
    seller_orders = Order.objects.filter(items__product__seller=request.user).distinct()
    total_orders = seller_orders.count()
    pending_orders = seller_orders.filter(status='pending').count()
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
    }
    
    return render(request, 'store/seller_dashboard.html', context)

@login_required
def buyer_dashboard(request):
    """Buyer dashboard view"""
    # Check if user has buyer profile
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'buyer':
            messages.error(request, 'ليس لديك صلاحية الوصول إلى لوحة تحكم المشتري')
            return redirect('home')
    except:
        # If no profile, assume it's a buyer
        pass
    
    # Import models
    Order = apps.get_model('store', 'Order')
    
    # Get buyer-specific statistics
    user_orders = Order.objects.filter(user=request.user)
    total_orders = user_orders.count()
    pending_orders = user_orders.filter(status='pending').count()
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
    }
    
    return render(request, 'store/buyer_dashboard.html', context)

def seller_products(request):
    """Seller products view"""
    return render(request, 'store/seller_products.html')

def add_product(request):
    """Add product view"""
    return render(request, 'store/add_product.html')

def edit_product(request, product_id):
    """Edit product view"""
    return render(request, 'store/edit_product.html')

def delete_product(request, product_id):
    """Delete product view"""
    return redirect('seller_products')

def seller_orders(request):
    """Seller orders view"""
    return render(request, 'store/seller_orders.html')

def seller_order_detail(request, order_id):
    """Seller order detail view"""
    return render(request, 'store/seller_order_detail.html')

def update_order_status(request, order_id):
    """Update order status view"""
    return redirect('seller_orders')

def seller_reports(request):
    """Seller reports view"""
    return render(request, 'store/seller_reports.html')

def inventory_management(request):
    """Inventory management view"""
    return render(request, 'store/inventory_management.html')

def smart_inventory_reports(request):
    """Smart inventory reports view"""
    return render(request, 'store/smart_inventory_reports.html')

def seller_performance_analytics(request):
    """Seller performance analytics view"""
    return render(request, 'store/seller_performance_analytics.html')

def view_commissions(request):
    """View commissions"""
    return render(request, 'store/commissions.html')

def pay_commission(request, commission_id):
    """Pay commission"""
    return redirect('view_commissions')

def commission_report(request):
    """Commission report view"""
    return render(request, 'store/commission_report.html')

def manage_sellers(request):
    """Manage sellers view"""
    return render(request, 'store/manage_sellers.html')

def open_dispute(request, order_id):
    """Open dispute view"""
    return render(request, 'store/open_dispute.html')

def manage_disputes(request):
    """Manage disputes view"""
    return render(request, 'store/manage_disputes.html')

def advanced_reports(request):
    """Advanced reports view"""
    return render(request, 'store/advanced_reports.html')

def ai_analytics_dashboard(request):
    """AI analytics dashboard view"""
    return render(request, 'store/ai_analytics_dashboard.html')

def financial_reports(request):
    """Financial reports view"""
    return render(request, 'store/financial_reports.html')

def view_wishlist(request):
    """View wishlist"""
    return render(request, 'store/wishlist.html')

def add_to_wishlist(request, product_id):
    """Add to wishlist"""
    return redirect('view_wishlist')

def remove_from_wishlist(request, product_id):
    """Remove from wishlist"""
    return redirect('view_wishlist')

def add_review(request, product_id):
    """Add review"""
    return redirect('product_detail', pk=product_id)

def delete_review(request, review_id):
    """Delete review"""
    return redirect('product_detail', pk=request.GET.get('product_id', 1))

def view_comparison(request):
    """View comparison"""
    return render(request, 'store/product_comparison.html')

def add_to_comparison(request, product_id):
    """Add to comparison"""
    return redirect('view_comparison')

def remove_from_comparison(request, product_id):
    """Remove from comparison"""
    return redirect('view_comparison')

def advanced_search(request):
    """Advanced search view"""
    return render(request, 'store/advanced_search.html')

def payment_view(request, order_id):
    """Payment view"""
    return render(request, 'store/payment.html')

def create_stripe_payment_intent(request, order_id):
    """Create Stripe payment intent"""
    return JsonResponse({'status': 'success'})

def create_paypal_payment(request, order_id):
    """Create PayPal payment"""
    return JsonResponse({'status': 'success'})

def execute_paypal_payment(request, payment_id):
    """Execute PayPal payment"""
    return JsonResponse({'status': 'success'})

def stripe_webhook(request):
    """Stripe webhook"""
    return HttpResponse(status=200)

def apply_coupon(request):
    """Apply coupon"""
    return JsonResponse({'status': 'success'})

def remove_coupon(request):
    """Remove coupon"""
    return JsonResponse({'status': 'success'})

def coupon_management(request):
    """Coupon management view"""
    return render(request, 'store/coupon_management.html')

def delete_coupon(request, coupon_id):
    """Delete coupon"""
    return redirect('coupon_management')

def loyalty_dashboard(request):
    """Loyalty dashboard view"""
    return render(request, 'store/loyalty_dashboard.html')

def redeem_reward(request, reward_id):
    """Redeem reward"""
    return redirect('loyalty_dashboard')

def loyalty_program_management(request):
    """Loyalty program management view"""
    return render(request, 'store/loyalty_program_management.html')

def delete_loyalty_reward(request, reward_id):
    """Delete loyalty reward"""
    return redirect('loyalty_program_management')

def email_campaigns(request):
    """Email campaigns view"""
    return render(request, 'store/email_campaigns.html')

def send_email_campaign(request, campaign_id):
    """Send email campaign"""
    return redirect('email_campaigns')

def delete_email_campaign(request, campaign_id):
    """Delete email campaign"""
    return redirect('email_campaigns')

def get_recommendations(request):
    """Get recommendations"""
    return render(request, 'store/recommendations.html')

def track_user_behavior(request):
    """Track user behavior"""
    return JsonResponse({'status': 'success'})

def advertising_campaigns(request):
    """Advertising campaigns view"""
    return render(request, 'store/advertising_campaigns.html')

def delete_advertising_campaign(request, campaign_id):
    """Delete advertising campaign"""
    return redirect('advertising_campaigns')

def social_media_integration(request):
    """Social media integration view"""
    return render(request, 'store/social_media_integration.html')

def delete_social_media_integration(request, integration_id):
    """Delete social media integration"""
    return redirect('social_media_integration')

def shipping_integration(request):
    """Shipping integration view"""
    return render(request, 'store/shipping_integration.html')

def delete_shipping_integration(request, integration_id):
    """Delete shipping integration"""
    return redirect('shipping_integration')

def external_inventory(request):
    """External inventory view"""
    return render(request, 'store/external_inventory.html')

def delete_external_inventory(request, inventory_id):
    """Delete external inventory"""
    return redirect('external_inventory')

def accounting_integration(request):
    """Accounting integration view"""
    return render(request, 'store/accounting_integration.html')

def delete_accounting_integration(request, integration_id):
    """Delete accounting integration"""
    return redirect('accounting_integration')

def analytics_integration(request):
    """Analytics integration view"""
    # Import models
    from django.apps import apps
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    AnalyticsIntegration = apps.get_model('store', 'AnalyticsIntegration')
    
    # Get analytics data
    total_events = AnalyticsIntegration.objects.count()
    
    # Get event types with counts
    event_types = AnalyticsIntegration.objects.values('event_type').annotate(
        count=Count('event_type')
    ).order_by('-count')
    
    # Get recent events (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    analytics_events = AnalyticsIntegration.objects.filter(
        timestamp__gte=thirty_days_ago
    ).order_by('-timestamp')[:50]
    
    context = {
        'total_events': total_events,
        'event_types': event_types,
        'analytics_events': analytics_events,
    }
    
    return render(request, 'store/analytics_integration.html', context)

def track_analytics_event(request):
    """Track analytics event"""
    return JsonResponse({'status': 'success'})

def debug_manager_access(request):
    """Debug manager access view"""
    context = {
        'user_authenticated': request.user.is_authenticated,
        'user_username': request.user.username if hasattr(request.user, 'username') else 'Not authenticated',
    }
    return render(request, 'store/debug_manager.html', context)

def debug_manager_dashboard(request):
    """Debug manager dashboard view"""
    # Import models
    Product = apps.get_model('store', 'Product')
    Order = apps.get_model('store', 'Order')
    
    # Get statistics
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
    }
    return render(request, 'store/manager_dashboard.html', context)
