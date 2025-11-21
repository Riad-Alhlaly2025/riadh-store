# Essential views.py file with required functions for dashboard access

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.apps import apps
from django.db.models import Sum, Count, Avg
import logging
import json
from .utils import Cart

logger = logging.getLogger(__name__)

def home(request):
    """Home page view"""
    return render(request, 'store/home.html')

from django.core.cache import cache

def product_list(request):
    """Product list view with caching and pagination"""
    # Get page number from request
    page = request.GET.get('page', 1)
    
    # Try to get products from cache first
    cache_key = f'product_list_page_{page}'
    products = cache.get(cache_key)
    
    if products is None:
        Product = apps.get_model('store', 'Product')
        products_list = Product.objects.all().select_related('seller')
        
        # Implement pagination
        from django.core.paginator import Paginator
        paginator = Paginator(products_list, 12)  # 12 products per page
        try:
            products = paginator.page(page)
        except:
            products = paginator.page(1)
        
        # Cache for 15 minutes
        cache.set(cache_key, products, 60 * 15)
    
    return render(request, 'store/product_list.html', {'products': products})

def product_detail(request, pk):
    """Product detail view with caching"""
    # Try to get product from cache first
    cache_key = f'product_detail_{pk}'
    product = cache.get(cache_key)
    
    if product is None:
        Product = apps.get_model('store', 'Product')
        product = get_object_or_404(Product, pk=pk)
        # Cache for 30 minutes
        cache.set(cache_key, product, 60 * 30)
    
    return render(request, 'store/product_detail.html', {'product': product})

def view_cart(request):
    """View cart with optimized queries"""
    cart = Cart(request.session)
    cart_items = cart.get_items()
    total_price = cart.get_total_price()
    
    # Store cart total in session for coupon calculations
    request.session['cart_total'] = str(total_price)
    
    context = {
        'cart_items': cart_items,
        'cart_total': total_price
    }
    
    return render(request, 'store/cart_with_coupons.html', context)

def add_to_cart(request, product_id):
    """Add product to cart"""
    if request.method == 'POST':
        # Get quantity from form data, default to 1
        quantity = int(request.POST.get('quantity', 1))
        
        # Use Cart class to add product
        cart = Cart(request.session)
        cart.add(product_id, quantity)
        
        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'تمت إضافة المنتج إلى السلة بنجاح!'})
    
    return redirect('view_cart')

def remove_from_cart(request, product_id):
    """Remove product from cart"""
    if request.method == 'POST':
        # Use Cart class to remove product
        cart = Cart(request.session)
        cart.remove(product_id)
        
        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'تمت إزالة المنتج من السلة بنجاح!'})
    
    return redirect('view_cart')

def update_cart(request, product_id):
    """Update cart item"""
    if request.method == 'POST':
        # Get quantity from JSON data
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
        except (json.JSONDecodeError, ValueError, TypeError):
            quantity = 1
        
        # Use Cart class to update product quantity
        cart = Cart(request.session)
        cart.update(product_id, quantity)
        
        # Return JSON response
        return JsonResponse({'success': True, 'message': 'تم تحديث السلة بنجاح!'})
    
    return redirect('view_cart')

def create_order(request):
    """Create order with coupon and loyalty support"""
    if request.method == 'POST':
        try:
            from decimal import Decimal
            from django.apps import apps
            from django.utils import timezone
            from .utils.coupon_utils import (
                apply_coupon_to_order, 
                calculate_earned_points, 
                update_user_loyalty_points
            )
            
            # Get form data
            full_name = request.POST.get('full_name', '')
            phone = request.POST.get('phone', '')
            address = request.POST.get('address', '')
            city = request.POST.get('city', '')
            state = request.POST.get('state', '')
            zip_code = request.POST.get('zip_code', '')
            payment_method = request.POST.get('payment_method', 'cash_on_delivery')
            
            # Validate required fields
            if not all([full_name, phone, address, city]):
                messages.error(request, 'يرجى ملء جميع الحقول المطلوبة')
                return redirect('checkout')
            
            # Get cart data
            cart = Cart(request.session)
            cart_items = cart.get_items()
            
            if not cart_items:
                messages.error(request, 'السلة فارغة')
                return redirect('product_list')
            
            # Calculate order total
            subtotal = cart.get_total_price()
            
            # Apply discounts
            coupon_discount = Decimal('0.00')
            loyalty_discount = Decimal('0.00')
            rewards_discount = Decimal('0.00')
            
            # Apply coupon if present
            if 'coupon_id' in request.session:
                try:
                    Coupon = apps.get_model('store', 'Coupon')
                    coupon = Coupon.objects.get(id=request.session['coupon_id'])
                    # Create temporary order for discount calculation
                    Order = apps.get_model('store', 'Order')
                    temp_order = Order(total_amount=subtotal)
                    coupon_discount = apply_coupon_to_order(temp_order, coupon.code)
                except:
                    pass  # Invalid coupon
            
            # Calculate final total
            total_discount = coupon_discount + loyalty_discount + rewards_discount
            final_total = max(subtotal - total_discount, Decimal('0.00'))
            
            # Create order
            Order = apps.get_model('store', 'Order')
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                total_amount=final_total,
                shipping_address=f"{address}, {city}, {state}, {zip_code}",
                phone_number=phone,
                status='pending'
            )
            
            # Create order items
            OrderItem = apps.get_model('store', 'OrderItem')
            Product = apps.get_model('store', 'Product')
            
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price
                )
                
                # Update product stock
                product = item['product']
                product.stock_quantity -= item['quantity']
                product.save()
            
            # Apply coupon usage
            if 'coupon_id' in request.session:
                try:
                    coupon = Coupon.objects.get(id=request.session['coupon_id'])
                    coupon.times_used += 1
                    coupon.save()
                except:
                    pass  # Invalid coupon
            
            # Calculate and award loyalty points
            if request.user.is_authenticated:
                points_earned = calculate_earned_points(order, request.user)
                update_user_loyalty_points(request.user, points_earned)
                
                # Deduct reward points if any rewards were used
                if 'rewards' in request.session:
                    LoyaltyProgram = apps.get_model('store', 'LoyaltyProgram')
                    try:
                        loyalty_program = LoyaltyProgram.objects.get(user=request.user)
                        for reward_data in request.session['rewards']:
                            loyalty_program.points -= reward_data.get('points_required', 0)
                        if loyalty_program.points < 0:
                            loyalty_program.points = 0
                        loyalty_program.save()
                    except:
                        pass  # Error updating loyalty points
            
            # Clear cart and session data
            cart.clear()
            if 'coupon_id' in request.session:
                del request.session['coupon_id']
            if 'discount_amount' in request.session:
                del request.session['discount_amount']
            if 'cart_total_with_discount' in request.session:
                del request.session['cart_total_with_discount']
            if 'rewards' in request.session:
                del request.session['rewards']
            request.session.modified = True
            
            messages.success(request, f'تم إنشاء الطلب بنجاح! رقم الطلب: {order.id}')
            return redirect('order_detail', order_id=order.id)
            
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            messages.error(request, 'حدث خطأ أثناء إنشاء الطلب')
            return redirect('checkout')
    
    return redirect('checkout')

def checkout(request):
    """Checkout view with coupon and loyalty support"""
    try:
        from decimal import Decimal
        from django.apps import apps
        
        # Import coupon utilities
        from .utils.coupon_utils import (
            apply_coupon_to_order, 
            calculate_loyalty_discount, 
            get_user_rewards,
            calculate_earned_points,
            update_user_loyalty_points
        )
        
        # Get cart data
        cart = Cart(request.session)
        cart_items = cart.get_items()
        subtotal = cart.get_total_price()
        
        # Initialize discount values
        coupon_discount = Decimal('0.00')
        loyalty_discount = Decimal('0.00')
        rewards_discount = Decimal('0.00')
        
        # Apply coupon if present in session
        if 'coupon_id' in request.session:
            try:
                Coupon = apps.get_model('store', 'Coupon')
                coupon = Coupon.objects.get(id=request.session['coupon_id'])
                # Create a temporary order object for discount calculation
                Order = apps.get_model('store', 'Order')
                temp_order = Order(total_amount=subtotal)
                coupon_discount = apply_coupon_to_order(temp_order, coupon.code)
            except:
                pass  # Invalid coupon, ignore
        
        # Apply loyalty discount if user is authenticated
        if request.user.is_authenticated:
            # Create a temporary order object for discount calculation
            Order = apps.get_model('store', 'Order')
            temp_order = Order(total_amount=subtotal)
            loyalty_discount = calculate_loyalty_discount(temp_order, request.user)
            
            # Get available rewards
            available_rewards = get_user_rewards(request.user)
            
            # Apply rewards discount if any rewards were selected
            if 'rewards' in request.session:
                for reward_data in request.session['rewards']:
                    if reward_data.get('type') == 'discount' and reward_data.get('discount_percentage'):
                        reward_discount = (subtotal * Decimal(reward_data['discount_percentage']) / 100).quantize(Decimal('0.01'))
                        rewards_discount += reward_discount
        
        # Calculate final total
        total_discount = coupon_discount + loyalty_discount + rewards_discount
        final_total = max(subtotal - total_discount, Decimal('0.00'))
        
        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'coupon_discount': coupon_discount,
            'loyalty_discount': loyalty_discount,
            'rewards_discount': rewards_discount,
            'total_discount': total_discount,
            'final_total': final_total,
            'available_rewards': get_user_rewards(request.user) if request.user.is_authenticated else []
        }
        
        return render(request, 'store/checkout_with_discounts.html', context)
        
    except Exception as e:
        logger.error(f"Error in checkout view: {str(e)}")
        return render(request, 'store/checkout_with_discounts.html', {
            'error': 'حدث خطأ أثناء تحميل صفحة الدفع'
        })

def order_detail(request, order_id):
    """Order detail view"""
    return render(request, 'store/order_detail.html')

def order_history(request):
    """Order history view"""
    # TODO: Implement actual order history functionality
    Order = apps.get_model('store', 'Order')
    if hasattr(request, 'user') and request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user)
        return render(request, 'store/order_history.html', {'orders': orders})
    else:
        messages.error(request, "يجب تسجيل الدخول لعرض تاريخ الطلبات")
        return redirect('home')

def notifications(request):
    """Notifications view"""
    # TODO: Implement actual notifications functionality
    Notification = apps.get_model('store', 'Notification')
    if hasattr(request, 'user') and request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user)
        return render(request, 'store/notifications.html', {'notifications': notifications})
    else:
        messages.error(request, "يجب تسجيل الدخول لعرض الإشعارات")
        return redirect('home')

def mark_notification_as_read(request, notification_id):
    """Mark notification as read"""
    # TODO: Implement actual notification marking functionality
    if request.method == 'POST':
        Notification = apps.get_model('store', 'Notification')
        try:
            notification = Notification.objects.get(pk=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'status': 'success', 'message': 'تم تحديث الإشعار'})
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'الإشعار غير موجود'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'طلب غير صالح'}, status=400)

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
    OrderItem = apps.get_model('store', 'OrderItem')
    Commission = apps.get_model('store', 'Commission')
    
    # Get seller-specific statistics
    seller_products = Product.objects.filter(seller=request.user)
    total_products = seller_products.count()
    
    # Get orders for seller's products
    seller_orders = Order.objects.filter(items__product__seller=request.user).distinct()
    total_orders = seller_orders.count()
    pending_orders = seller_orders.filter(status='pending').count()
    
    # Get commission data
    seller_commissions = Commission.objects.filter(user=request.user)
    total_commissions = seller_commissions.count()
    total_commission_amount = seller_commissions.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Get recent commissions
    recent_commissions = seller_commissions.order_by('-created_at')[:5]
    
    # Get sales data for charts
    # Monthly sales data
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                EXTRACT(month FROM o.created_at) as month,
                SUM(oi.quantity) as total_sales,
                SUM(oi.quantity * oi.price) as total_revenue
            FROM store_orderitem oi
            JOIN store_order o ON oi.order_id = o.id
            JOIN store_product p ON oi.product_id = p.id
            WHERE p.seller_id = %s
            GROUP BY EXTRACT(month FROM o.created_at)
            ORDER BY month
        """, [request.user.id])
        monthly_sales = cursor.fetchall()
    
    # Top selling products
    top_products = Product.objects.filter(seller=request.user).annotate(
        total_sold=Sum('orderitem__quantity')
    ).filter(total_sold__gt=0).order_by('-total_sold')[:5]
    
    # Order status distribution
    order_status_data = seller_orders.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Calculate seller performance metrics
    total_revenue = 0
    for sale in monthly_sales:
        total_revenue += sale[2] if sale[2] else 0
    
    # Calculate average order value
    if total_orders > 0:
        avg_order_value = total_revenue / total_orders
    else:
        avg_order_value = 0
    
    # Calculate seller level based on performance
    if total_revenue > 50000:
        seller_level = "ذهبي"
        seller_level_class = "gold"
    elif total_revenue > 20000:
        seller_level = "فضي"
        seller_level_class = "silver"
    else:
        seller_level = "برونزي"
        seller_level_class = "bronze"
    
    # Calculate seller rating (simulated)
    seller_rating = 4.8  # This would be calculated from actual reviews in a real implementation
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_commissions': total_commissions,
        'total_commission_amount': total_commission_amount,
        'recent_commissions': recent_commissions,
        'monthly_sales': monthly_sales,
        'top_products': top_products,
        'order_status_data': order_status_data,
        'currency': 'SAR',  # Default currency
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'seller_level': seller_level,
        'seller_level_class': seller_level_class,
        'seller_rating': seller_rating,
    }
    
    # Render the luxury dashboard template
    return render(request, 'store/seller_dashboard_luxury.html', context)

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
    """AI analytics dashboard view with comprehensive business intelligence"""
    # Import models
    from django.apps import apps
    from django.db.models import Count, Sum, Avg, Q
    from django.db.models.functions import TruncDay, TruncMonth
    from decimal import Decimal
    from datetime import datetime, timedelta
    
    # Get all required models
    Product = apps.get_model('store', 'Product')
    Order = apps.get_model('store', 'Order')
    OrderItem = apps.get_model('store', 'OrderItem')
    User = apps.get_model('auth', 'User')
    Commission = apps.get_model('store', 'Commission')
    AnalyticsIntegration = apps.get_model('store', 'AnalyticsIntegration')
    
    # Basic statistics
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()
    
    # Revenue calculations
    total_revenue = Order.objects.filter(status='delivered').aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')
    
    # Revenue in the last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    revenue_30_days = Order.objects.filter(
        status='delivered',
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Revenue in the last 7 days
    seven_days_ago = datetime.now() - timedelta(days=7)
    revenue_7_days = Order.objects.filter(
        status='delivered',
        created_at__gte=seven_days_ago
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Average order value
    avg_order_value = Order.objects.filter(status='delivered').aggregate(
        avg=Avg('total_amount')
    )['avg'] or Decimal('0.00')
    
    # Customer lifetime value (simplified)
    customer_lifetime_value = avg_order_value * Decimal('5')  # Assuming 5 purchases per customer
    
    # Conversion rates
    total_visitors = AnalyticsIntegration.objects.filter(event_type='page_view').count()
    total_purchases = Order.objects.count()
    conversion_rate = (total_purchases / total_visitors * 100) if total_visitors > 0 else 0
    
    # Cart to checkout conversion
    cart_additions = AnalyticsIntegration.objects.filter(event_type='add_to_cart').count()
    checkouts = AnalyticsIntegration.objects.filter(event_type='checkout').count()
    cart_conversion_rate = (checkouts / cart_additions * 100) if cart_additions > 0 else 0
    
    # Checkout to purchase conversion
    purchases = AnalyticsIntegration.objects.filter(event_type='purchase').count()
    checkout_conversion_rate = (purchases / checkouts * 100) if checkouts > 0 else 0
    
    # AI Predictions (simplified)
    predicted_orders_next_7_days = int(total_orders * 1.15)  # 15% growth prediction
    predicted_revenue_next_7_days = total_revenue * Decimal('1.20')  # 20% revenue growth prediction
    
    # User behavior analytics
    new_customers = User.objects.filter(
        date_joined__gte=thirty_days_ago
    ).count()
    
    returning_customers = User.objects.filter(
        order__created_at__lt=thirty_days_ago
    ).distinct().count()
    
    page_views = AnalyticsIntegration.objects.filter(event_type='page_view').count()
    product_views = AnalyticsIntegration.objects.filter(event_type='product_view').count()
    cart_additions = AnalyticsIntegration.objects.filter(event_type='add_to_cart').count()
    checkouts = AnalyticsIntegration.objects.filter(event_type='checkout').count()
    purchases = AnalyticsIntegration.objects.filter(event_type='purchase').count()
    searches = AnalyticsIntegration.objects.filter(event_type='search').count()
    
    # User statistics
    sellers_count = User.objects.filter(userprofile__role='seller').count()
    buyers_count = User.objects.filter(userprofile__role='buyer').count()
    managers_count = User.objects.filter(userprofile__role='manager').count()
    
    # Commission summary
    total_commission_amount = Commission.objects.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    paid_commissions = Commission.objects.filter(is_paid=True).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    pending_commissions = Commission.objects.filter(is_paid=False).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Sales by category
    category_sales = {}
    for category, _ in Product.CATEGORY_CHOICES:
        category_orders = OrderItem.objects.filter(
            product__category=category,
            order__status='delivered'
        )
        
        quantity = category_orders.aggregate(total=Sum('quantity'))['total'] or 0
        amount = category_orders.aggregate(total=Sum('price'))['total'] or Decimal('0.00')
        
        # Calculate percentage
        category_percentage = (float(amount) / float(total_revenue) * 100) if total_revenue > 0 else 0
        
        category_sales[category] = {
            'quantity': quantity,
            'amount': amount,
            'percentage': round(category_percentage, 2)
        }
    
    # Top selling products by quantity
    top_products_by_quantity = OrderItem.objects.values(
        'product_id', 'product__name', 'product__seller__username'
    ).annotate(
        quantity=Sum('quantity'),
        amount=Sum('price')
    ).order_by('-quantity')[:10]
    
    # Top selling products by revenue
    top_products_by_revenue = OrderItem.objects.values(
        'product_id', 'product__name', 'product__seller__username'
    ).annotate(
        quantity=Sum('quantity'),
        amount=Sum('price')
    ).order_by('-amount')[:10]
    
    # Prepare context
    context = {
        # Basic statistics
        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users,
        'total_revenue': total_revenue,
        
        # Revenue analytics
        'revenue_30_days': revenue_30_days,
        'revenue_7_days': revenue_7_days,
        'avg_order_value': avg_order_value,
        'customer_lifetime_value': customer_lifetime_value,
        
        # AI Predictions
        'predicted_orders_next_7_days': predicted_orders_next_7_days,
        'predicted_revenue_next_7_days': predicted_revenue_next_7_days,
        
        # Conversion analytics
        'conversion_rate': round(conversion_rate, 2),
        'cart_conversion_rate': round(cart_conversion_rate, 2),
        'checkout_conversion_rate': round(checkout_conversion_rate, 2),
        
        # User behavior analytics
        'new_customers': new_customers,
        'returning_customers': returning_customers,
        'page_views': page_views,
        'product_views': product_views,
        'cart_additions': cart_additions,
        'checkouts': checkouts,
        'purchases': purchases,
        'searches': searches,
        
        # User statistics
        'sellers_count': sellers_count,
        'buyers_count': buyers_count,
        'managers_count': managers_count,
        
        # Commission summary
        'total_commission_amount': total_commission_amount,
        'paid_commissions': paid_commissions,
        'pending_commissions': pending_commissions,
        
        # Sales by category
        'category_sales': category_sales,
        
        # Top products
        'top_products_by_quantity': top_products_by_quantity,
        'top_products_by_revenue': top_products_by_revenue,
    }
    
    return render(request, 'store/ai_analytics_dashboard.html', context)

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
    """Advanced search view with faceted filtering"""
    from django.apps import apps
    from django.db.models import Q, Min, Max
    from decimal import Decimal
    
    Product = apps.get_model('store', 'Product')
    
    # Get search parameters
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort_by', 'name')
    
    # Start with all products
    products = Product.objects.all()
    
    # Apply search query
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(seo_keywords__icontains=query)
        )
    
    # Apply category filter
    if category:
        products = products.filter(category=category)
    
    # Apply price filters
    if min_price:
        products = products.filter(price__gte=Decimal(min_price))
    if max_price:
        products = products.filter(price__lte=Decimal(max_price))
    
    # Apply sorting
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    
    # Get price range for filter UI
    price_range = Product.objects.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    context = {
        'products': products,
        'query': query,
        'category': category,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'price_range': price_range,
        'categories': Product.CATEGORY_CHOICES,
    }
    
    return render(request, 'store/advanced_search.html', context)

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
    """Apply coupon to cart"""
    if request.method == 'POST':
        try:
            # Get coupon code from form data
            coupon_code = request.POST.get('coupon_code', '').strip()
            
            if not coupon_code:
                return JsonResponse({'status': 'error', 'message': 'يرجى إدخال رمز الكوبون'})
            
            # Import models
            from django.apps import apps
            from decimal import Decimal
            from django.utils import timezone
            
            Coupon = apps.get_model('store', 'Coupon')
            Cart = apps.get_model('store', 'Cart')  # Assuming there's a Cart model
            
            # Get coupon
            try:
                coupon = Coupon.objects.get(
                    code=coupon_code,
                    active=True,
                    valid_from__lte=timezone.now(),
                    valid_to__gte=timezone.now()
                )
            except Coupon.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'الكوبون غير صالح أو منتهي الصلاحية'})
            
            # Check usage limit
            if coupon.usage_limit and coupon.times_used >= coupon.usage_limit:
                return JsonResponse({'status': 'error', 'message': 'الكوبون تجاوز حد الاستخدام'})
            
            # Store coupon in session
            request.session['coupon_id'] = coupon.id
            
            # Calculate discount
            cart_total = Decimal(request.session.get('cart_total', 0))
            discount_amount = Decimal('0.00')
            
            if coupon.discount_type == 'percentage':
                discount_amount = (cart_total * coupon.discount_value / 100).quantize(Decimal('0.01'))
            else:  # fixed amount
                discount_amount = min(coupon.discount_value, cart_total)
            
            # Calculate new total
            new_total = cart_total - discount_amount
            
            # Update session with discount info
            request.session['discount_amount'] = str(discount_amount)
            request.session['cart_total_with_discount'] = str(new_total)
            
            return JsonResponse({
                'status': 'success',
                'message': f'تم تطبيق الكوبون بنجاح! تم خصم {discount_amount} ر.س',
                'discount_amount': str(discount_amount),
                'new_total': str(new_total)
            })
            
        except Exception as e:
            logger.error(f"Error applying coupon: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'حدث خطأ أثناء تطبيق الكوبون'})
    
    return JsonResponse({'status': 'error', 'message': 'طلب غير صالح'})

def remove_coupon(request):
    """Remove coupon from cart"""
    if request.method == 'POST':
        try:
            # Remove coupon from session
            if 'coupon_id' in request.session:
                del request.session['coupon_id']
            
            if 'discount_amount' in request.session:
                del request.session['discount_amount']
                
            if 'cart_total_with_discount' in request.session:
                del request.session['cart_total_with_discount']
            
            # Get original cart total
            cart_total = request.session.get('cart_total', 0)
            
            return JsonResponse({
                'status': 'success',
                'message': 'تم إزالة الكوبون بنجاح',
                'new_total': str(cart_total)
            })
        except Exception as e:
            logger.error(f"Error removing coupon: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'حدث خطأ أثناء إزالة الكوبون'})
    
    return JsonResponse({'status': 'error', 'message': 'طلب غير صالح'})

def coupon_management(request):
    """Coupon management view"""
    if request.method == 'POST':
        try:
            # Import models
            from django.apps import apps
            from decimal import Decimal
            from django.utils import timezone
            from datetime import datetime
            
            Coupon = apps.get_model('store', 'Coupon')
            
            # Get form data
            code = request.POST.get('code', '').strip()
            discount_type = request.POST.get('discount_type', 'percentage')
            discount_value = request.POST.get('discount_value', '0')
            minimum_amount = request.POST.get('minimum_amount', '0')
            valid_from = request.POST.get('valid_from', '')
            valid_to = request.POST.get('valid_to', '')
            usage_limit = request.POST.get('usage_limit', '')
            
            # Validate required fields
            if not code:
                messages.error(request, 'يرجى إدخال رمز الكوبون')
                return redirect('coupon_management')
            
            # Check if coupon code already exists
            if Coupon.objects.filter(code=code).exists():
                messages.error(request, 'رمز الكوبون موجود بالفعل')
                return redirect('coupon_management')
            
            # Parse datetime fields
            try:
                valid_from_dt = datetime.fromisoformat(valid_from.replace('T', ' '))
                valid_to_dt = datetime.fromisoformat(valid_to.replace('T', ' '))
            except ValueError:
                messages.error(request, 'صيغة التاريخ غير صحيحة')
                return redirect('coupon_management')
            
            # Create coupon
            coupon = Coupon.objects.create(
                code=code,
                discount_type=discount_type,
                discount_value=Decimal(discount_value),
                minimum_amount=Decimal(minimum_amount),
                valid_from=valid_from_dt,
                valid_to=valid_to_dt,
                usage_limit=int(usage_limit) if usage_limit else None,
                active=True
            )
            
            messages.success(request, f'تم إنشاء الكوبون "{code}" بنجاح')
            return redirect('coupon_management')
            
        except Exception as e:
            logger.error(f"Error creating coupon: {str(e)}")
            messages.error(request, 'حدث خطأ أثناء إنشاء الكوبون')
            return redirect('coupon_management')
    
    # GET request - display coupons
    try:
        from django.apps import apps
        Coupon = apps.get_model('store', 'Coupon')
        coupons = Coupon.objects.all().order_by('-created_at')
        return render(request, 'store/coupon_management.html', {'coupons': coupons})
    except Exception as e:
        logger.error(f"Error loading coupons: {str(e)}")
        messages.error(request, 'حدث خطأ أثناء تحميل الكوبونات')
        return render(request, 'store/coupon_management.html', {'coupons': []})

def delete_coupon(request, coupon_id):
    """Delete coupon"""
    if request.method == 'POST':
        try:
            from django.apps import apps
            Coupon = apps.get_model('store', 'Coupon')
            
            coupon = get_object_or_404(Coupon, id=coupon_id)
            coupon_name = coupon.code
            coupon.delete()
            
            messages.success(request, f'تم حذف الكوبون "{coupon_name}" بنجاح')
        except Exception as e:
            logger.error(f"Error deleting coupon: {str(e)}")
            messages.error(request, 'حدث خطأ أثناء حذف الكوبون')
    
    return redirect('coupon_management')

def loyalty_dashboard(request):
    """Loyalty dashboard view"""
    try:
        from django.apps import apps
        from django.db.models import Sum
        LoyaltyProgram = apps.get_model('store', 'LoyaltyProgram')
        LoyaltyReward = apps.get_model('store', 'LoyaltyReward')
        Order = apps.get_model('store', 'Order')
        
        # Get or create loyalty program for user
        loyalty_program, created = LoyaltyProgram.objects.get_or_create(
            user=request.user,
            defaults={
                'points': 0,
                'level': 'bronze',
                'total_spent': 0
            }
        )
        
        # Calculate user rank
        user_rank = LoyaltyProgram.objects.filter(
            points__gt=loyalty_program.points
        ).count() + 1
        
        # Get available rewards
        rewards = LoyaltyReward.objects.filter(active=True).order_by('points_required')
        
        context = {
            'loyalty_program': loyalty_program,
            'loyalty_rank': user_rank,
            'rewards': rewards
        }
        
        return render(request, 'store/loyalty_dashboard.html', context)
    except Exception as e:
        logger.error(f"Error loading loyalty dashboard: {str(e)}")
        messages.error(request, 'حدث خطأ أثناء تحميل لوحة تحكم الولاء')
        return render(request, 'store/loyalty_dashboard.html', {
            'loyalty_program': None,
            'loyalty_rank': 0,
            'rewards': []
        })

def redeem_reward(request, reward_id):
    """Redeem reward"""
    if request.method == 'POST':
        try:
            from django.apps import apps
            LoyaltyProgram = apps.get_model('store', 'LoyaltyProgram')
            LoyaltyReward = apps.get_model('store', 'LoyaltyReward')
            
            # Get user's loyalty program
            loyalty_program = get_object_or_404(LoyaltyProgram, user=request.user)
            
            # Get reward
            reward = get_object_or_404(LoyaltyReward, id=reward_id, active=True)
            
            # Check if user has enough points
            if loyalty_program.points < reward.points_required:
                messages.error(request, 'ليس لديك نقاط كافية لاستبدال هذه المكافأة')
                return redirect('loyalty_dashboard')
            
            # Deduct points
            loyalty_program.points -= reward.points_required
            loyalty_program.save()
            
            # Add reward code to session for use in checkout
            if 'rewards' not in request.session:
                request.session['rewards'] = []
            
            request.session['rewards'].append({
                'id': reward.id,
                'name': reward.name,
                'type': reward.reward_type,
                'discount_percentage': str(reward.discount_percentage) if reward.discount_percentage else None
            })
            
            # Mark session as modified
            request.session.modified = True
            
            messages.success(request, f'تم استبدال المكافأة "{reward.name}" بنجاح!')
            return redirect('loyalty_dashboard')
            
        except Exception as e:
            logger.error(f"Error redeeming reward: {str(e)}")
            messages.error(request, 'حدث خطأ أثناء استبدال المكافأة')
    
    return redirect('loyalty_dashboard')

def loyalty_program_management(request):
    """Loyalty program management view"""
    if request.method == 'POST':
        try:
            # Import models
            from django.apps import apps
            from decimal import Decimal
            
            LoyaltyReward = apps.get_model('store', 'LoyaltyReward')
            
            # Get form data
            name = request.POST.get('name', '').strip()
            reward_type = request.POST.get('reward_type', 'discount')
            points_required = request.POST.get('points_required', '0')
            discount_percentage = request.POST.get('discount_percentage', '')
            
            # Validate required fields
            if not name:
                messages.error(request, 'يرجى إدخال اسم المكافأة')
                return redirect('loyalty_program_management')
            
            # Create reward
            reward = LoyaltyReward.objects.create(
                name=name,
                reward_type=reward_type,
                points_required=int(points_required),
                discount_percentage=Decimal(discount_percentage) if discount_percentage else None,
                active=True
            )
            
            messages.success(request, f'تم إنشاء المكافأة "{name}" بنجاح')
            return redirect('loyalty_program_management')
            
        except Exception as e:
            logger.error(f"Error creating loyalty reward: {str(e)}")
            messages.error(request, 'حدث خطأ أثناء إنشاء المكافأة')
            return redirect('loyalty_program_management')
    
    # GET request - display rewards
    try:
        from django.apps import apps
        LoyaltyReward = apps.get_model('store', 'LoyaltyReward')
        rewards = LoyaltyReward.objects.all().order_by('-created_at')
        return render(request, 'store/loyalty_program_management.html', {'rewards': rewards})
    except Exception as e:
        logger.error(f"Error loading loyalty rewards: {str(e)}")
        messages.error(request, 'حدث خطأ أثناء تحميل المكافآت')
        return render(request, 'store/loyalty_program_management.html', {'rewards': []})

def delete_loyalty_reward(request, reward_id):
    """Delete loyalty reward"""
    if request.method == 'POST':
        try:
            from django.apps import apps
            LoyaltyReward = apps.get_model('store', 'LoyaltyReward')
            
            reward = get_object_or_404(LoyaltyReward, id=reward_id)
            reward_name = reward.name
            reward.delete()
            
            messages.success(request, f'تم حذف المكافأة "{reward_name}" بنجاح')
        except Exception as e:
            logger.error(f"Error deleting loyalty reward: {str(e)}")
            messages.error(request, 'حدث خطأ أثناء حذف المكافأة')
    
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
    from django.db.models import Count, Q, Sum
    from datetime import datetime, timedelta
    
    AnalyticsIntegration = apps.get_model('store', 'AnalyticsIntegration')
    Order = apps.get_model('store', 'Order')
    Product = apps.get_model('store', 'Product')
    User = apps.get_model('auth', 'User')
    
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
    
    # Get conversion data
    total_visitors = AnalyticsIntegration.objects.filter(event_type='page_view').count()
    total_purchases = Order.objects.count()
    conversion_rate = (total_purchases / total_visitors * 100) if total_visitors > 0 else 0
    
    # Get top products by views
    top_products = Product.objects.annotate(
        view_count=Count('analyticsintegration')
    ).filter(view_count__gt=0).order_by('-view_count')[:10]
    
    # Get user engagement data
    active_users = User.objects.filter(
        analyticsintegration__timestamp__gte=thirty_days_ago
    ).distinct().count()
    
    context = {
        'total_events': total_events,
        'event_types': event_types,
        'analytics_events': analytics_events,
        'conversion_rate': round(conversion_rate, 2),
        'total_visitors': total_visitors,
        'total_purchases': total_purchases,
        'top_products': top_products,
        'active_users': active_users,
    }
    
    return render(request, 'store/analytics_integration.html', context)

def track_analytics_event(request):
    """Track analytics event"""
    return JsonResponse({'status': 'success'})

def export_analytics_report(request, format):
    """Export analytics report in specified format"""
    from django.apps import apps
    from django.db.models import Count, Sum, Avg
    from decimal import Decimal
    from datetime import datetime, timedelta
    import csv
    import json
    from django.http import HttpResponse
    
    # Get all required models
    Product = apps.get_model('store', 'Product')
    Order = apps.get_model('store', 'Order')
    OrderItem = apps.get_model('store', 'OrderItem')
    User = apps.get_model('auth', 'User')
    Commission = apps.get_model('store', 'Commission')
    AnalyticsIntegration = apps.get_model('store', 'AnalyticsIntegration')
    
    # Get data for export
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()
    total_revenue = Order.objects.filter(status='delivered').aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')
    
    # User statistics
    sellers_count = User.objects.filter(userprofile__role='seller').count()
    buyers_count = User.objects.filter(userprofile__role='buyer').count()
    managers_count = User.objects.filter(userprofile__role='manager').count()
    
    # Sales data by category
    category_sales = {}
    for category, _ in Product.CATEGORY_CHOICES:
        category_orders = OrderItem.objects.filter(
            product__category=category,
            order__status='delivered'
        )
        
        quantity = category_orders.aggregate(total=Sum('quantity'))['total'] or 0
        amount = category_orders.aggregate(total=Sum('price'))['total'] or Decimal('0.00')
        
        category_sales[category] = {
            'quantity': quantity,
            'amount': amount
        }
    
    # Top selling products
    top_products = OrderItem.objects.values(
        'product_id', 'product__name'
    ).annotate(
        quantity=Sum('quantity'),
        amount=Sum('price')
    ).order_by('-quantity')[:10]
    
    # Order status distribution
    order_status_data = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="analytics_report.csv"'
        
        writer = csv.writer(response)
        
        # Write headers
        writer.writerow([
            'التقرير', 'القيمة', 'التاريخ'
        ])
        
        # Write basic statistics
        writer.writerow(['إجمالي المنتجات', total_products, datetime.now().strftime('%Y-%m-%d')])
        writer.writerow(['إجمالي الطلبات', total_orders, datetime.now().strftime('%Y-%m-%d')])
        writer.writerow(['إجمالي المستخدمين', total_users, datetime.now().strftime('%Y-%m-%d')])
        
        # Write revenue data
        writer.writerow(['إجمالي الإيرادات', str(total_revenue), datetime.now().strftime('%Y-%m-%d')])
        
        # Write user statistics
        writer.writerow(['عدد البائعين', sellers_count, datetime.now().strftime('%Y-%m-%d')])
        writer.writerow(['عدد المشترين', buyers_count, datetime.now().strftime('%Y-%m-%d')])
        writer.writerow(['عدد المديرين', managers_count, datetime.now().strftime('%Y-%m-%d')])
        
        # Write category sales data
        writer.writerow([])  # Empty row
        writer.writerow(['مبيعات حسب الفئة', '', ''])
        writer.writerow(['الفئة', 'الكمية', 'المبلغ'])
        for category, data in category_sales.items():
            writer.writerow([category, data['quantity'], str(data['amount'])])
        
        # Write top products
        writer.writerow([])  # Empty row
        writer.writerow(['أفضل المنتجات مبيعًا', '', ''])
        writer.writerow(['المنتج', 'الكمية', 'المبلغ'])
        for product in top_products:
            writer.writerow([product['product__name'], product['quantity'], str(product['amount'])])
        
        return response
    
    elif format == 'excel':
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="analytics_report.xls"'
        
        # Create a simple Excel-like format using HTML table
        response.write('<html><head><meta charset="utf-8"></head><body>')
        
        # Basic statistics table
        response.write('<h2>الإحصائيات الأساسية</h2>')
        response.write('<table border="1">')
        response.write('<tr><th>التقرير</th><th>القيمة</th><th>التاريخ</th></tr>')
        
        # Write basic statistics
        response.write(f'<tr><td>إجمالي المنتجات</td><td>{total_products}</td><td>{datetime.now().strftime("%Y-%m-%d")}</td></tr>')
        response.write(f'<tr><td>إجمالي الطلبات</td><td>{total_orders}</td><td>{datetime.now().strftime("%Y-%m-%d")}</td></tr>')
        response.write(f'<tr><td>إجمالي المستخدمين</td><td>{total_users}</td><td>{datetime.now().strftime("%Y-%m-%d")}</td></tr>')
        response.write(f'<tr><td>إجمالي الإيرادات</td><td>{total_revenue}</td><td>{datetime.now().strftime("%Y-%m-%d")}</td></tr>')
        response.write(f'<tr><td>عدد البائعين</td><td>{sellers_count}</td><td>{datetime.now().strftime("%Y-%m-%d")}</td></tr>')
        response.write(f'<tr><td>عدد المشترين</td><td>{buyers_count}</td><td>{datetime.now().strftime("%Y-%m-%d")}</td></tr>')
        response.write(f'<tr><td>عدد المديرين</td><td>{managers_count}</td><td>{datetime.now().strftime("%Y-%m-%d")}</td></tr>')
        
        response.write('</table>')
        
        # Category sales table
        response.write('<h2>مبيعات حسب الفئة</h2>')
        response.write('<table border="1">')
        response.write('<tr><th>الفئة</th><th>الكمية</th><th>المبلغ</th></tr>')
        for category, data in category_sales.items():
            response.write(f'<tr><td>{category}</td><td>{data["quantity"]}</td><td>{data["amount"]}</td></tr>')
        response.write('</table>')
        
        # Top products table
        response.write('<h2>أفضل المنتجات مبيعًا</h2>')
        response.write('<table border="1">')
        response.write('<tr><th>المنتج</th><th>الكمية</th><th>المبلغ</th></tr>')
        for product in top_products:
            response.write(f'<tr><td>{product["product__name"]}</td><td>{product["quantity"]}</td><td>{product["amount"]}</td></tr>')
        response.write('</table>')
        
        response.write('</body></html>')
        
        return response
    
    elif format == 'pdf':
        # For PDF, we'll return a simple text format for now
        # In a production environment, you would use a library like ReportLab
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="analytics_report.pdf"'
        
        # Create a simple text report
        report_content = f"""
        تقرير تحليلات المتجر
        ======================
        
        تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        إحصائيات أساسية:
        ----------------
        إجمالي المنتجات: {total_products}
        إجمالي الطلبات: {total_orders}
        إجمالي المستخدمين: {total_users}
        إجمالي الإيرادات: {total_revenue} ر.س
        
        إحصائيات المستخدمين:
        -------------------
        عدد البائعين: {sellers_count}
        عدد المشترين: {buyers_count}
        عدد المديرين: {managers_count}
        
        مبيعات حسب الفئة:
        ----------------
        """
        
        for category, data in category_sales.items():
            report_content += f"        {category}: {data['quantity']} وحدة، {data['amount']} ر.س\n"
        
        report_content += "\n        أفضل المنتجات مبيعًا:\n        -------------------\n"
        
        for product in top_products:
            report_content += f"        {product['product__name']}: {product['quantity']} وحدة، {product['amount']} ر.س\n"
        
        report_content += "\n        ملاحظة: هذا تقرير نصي بسيط. في بيئة الإنتاج، سيتم استخدام مكتبة متخصصة لإنشاء ملفات PDF."
        
        response.write(report_content)
        return response
    
    elif format == 'json':
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="analytics_report.json"'
        
        # Create JSON report
        report_data = {
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'basic_statistics': {
                'total_products': total_products,
                'total_orders': total_orders,
                'total_users': total_users,
                'total_revenue': str(total_revenue)
            },
            'user_statistics': {
                'sellers_count': sellers_count,
                'buyers_count': buyers_count,
                'managers_count': managers_count
            },
            'category_sales': category_sales,
            'top_products': list(top_products),
            'order_status_distribution': list(order_status_data)
        }
        
        response.write(json.dumps(report_data, ensure_ascii=False, indent=2))
        return response
    
    # For unsupported formats, return JSON
    return JsonResponse({'status': 'error', 'message': 'Unsupported format'})

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

def create_apple_pay_payment(request, order_id):
    """Create Apple Pay payment"""
    if request.method == 'POST':
        try:
            import json
            from django.apps import apps
            from decimal import Decimal
            
            # Get order
            Order = apps.get_model('store', 'Order')
            order = get_object_or_404(Order, id=order_id)
            
            # In a real implementation, you would:
            # 1. Validate the Apple Pay token
            # 2. Process the payment through Apple Pay API
            # 3. Create a Payment record
            # 4. Update order status
            
            # For now, we'll simulate a successful payment
            Payment = apps.get_model('store', 'Payment')
            payment = Payment.objects.create(
                order=order,
                payment_method='apple_pay',
                transaction_id=f"apple_pay_{order_id}_{int(time.time())}",
                amount=order.total_amount,
                currency=order.items.first().product.currency if order.items.exists() else 'USD',
                status='completed'
            )
            
            # Update order status
            order.status = 'processing'
            order.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'تم الدفع بنجاح',
                'payment_id': payment.id
            })
            
        except Exception as e:
            logger.error(f"Error processing Apple Pay payment: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'حدث خطأ أثناء معالجة الدفع'
            })
    
    return JsonResponse({'status': 'error', 'message': 'طلب غير صالح'})

def create_google_pay_payment(request, order_id):
    """Create Google Pay payment"""
    if request.method == 'POST':
        try:
            import json
            from django.apps import apps
            from decimal import Decimal
            
            # Get order
            Order = apps.get_model('store', 'Order')
            order = get_object_or_404(Order, id=order_id)
            
            # In a real implementation, you would:
            # 1. Validate the Google Pay token
            # 2. Process the payment through Google Pay API
            # 3. Create a Payment record
            # 4. Update order status
            
            # For now, we'll simulate a successful payment
            Payment = apps.get_model('store', 'Payment')
            payment = Payment.objects.create(
                order=order,
                payment_method='google_pay',
                transaction_id=f"google_pay_{order_id}_{int(time.time())}",
                amount=order.total_amount,
                currency=order.items.first().product.currency if order.items.exists() else 'USD',
                status='completed'
            )
            
            # Update order status
            order.status = 'processing'
            order.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'تم الدفع بنجاح',
                'payment_id': payment.id
            })
            
        except Exception as e:
            logger.error(f"Error processing Google Pay payment: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'حدث خطأ أثناء معالجة الدفع'
            })
    
    return JsonResponse({'status': 'error', 'message': 'طلب غير صالح'})

def cash_on_delivery_payment(request, order_id):
    """Process cash on delivery payment"""
    if request.method == 'POST':
        try:
            from django.apps import apps
            
            # Get order
            Order = apps.get_model('store', 'Order')
            order = get_object_or_404(Order, id=order_id)
            
            # Create payment record for cash on delivery
            Payment = apps.get_model('store', 'Payment')
            payment = Payment.objects.create(
                order=order,
                payment_method='cash_on_delivery',
                transaction_id=f"cod_{order_id}_{int(time.time())}",
                amount=order.total_amount,
                currency=order.items.first().product.currency if order.items.exists() else 'USD',
                status='pending'  # COD payments are pending until delivery
            )
            
            # Update order status
            order.status = 'processing'
            order.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'تم تأكيد الطلب للدفع عند الاستلام',
                'payment_id': payment.id
            })
            
        except Exception as e:
            logger.error(f"Error processing COD payment: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'حدث خطأ أثناء معالجة الطلب'
            })
    
    return JsonResponse({'status': 'error', 'message': 'طلب غير صالح'})
