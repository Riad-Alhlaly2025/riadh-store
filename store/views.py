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
from datetime import datetime
import os

logger = logging.getLogger(__name__)

def home(request):
    """Home page view with caching"""
    # Try to get home page data from cache first
    cache_key = 'home_page_data'
    home_data = cache.get(cache_key)
    
    if home_data is None:
        # If not in cache, prepare the data
        from django.apps import apps
        Product = apps.get_model('store', 'Product')
        
        # Get featured products (first 4 products as examples)
        try:
            featured_products = Product.objects.select_related('seller').all()[:4]
        except Exception as e:
            # If there's an error, create empty list
            featured_products = []
        
        home_data = {
            'featured_products': featured_products
        }
        
        # Cache for 10 minutes
        cache.set(cache_key, home_data, 60 * 10)
    
    return render(request, 'store/home.html', home_data)

from django.core.cache import cache
from store.services.cache_service import cache_service

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
    """Product detail view with caching and enhanced reviews system"""
    # Try to get product from cache first
    cache_key = f'product_detail_{pk}'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        Product = apps.get_model('store', 'Product')
        product = get_object_or_404(Product, pk=pk)
        
        # Get product reviews
        from .models import EnhancedReview
        reviews = EnhancedReview.objects.filter(product=product, is_verified_purchase=True)
        
        # Calculate average rating
        if reviews.exists():
            average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            review_count = reviews.count()
            
            # Calculate rating distribution
            rating_distribution = {}
            for i in range(1, 6):
                rating_distribution[i] = reviews.filter(rating=i).count()
        else:
            average_rating = 0
            review_count = 0
            rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        # Get top reviews (featured)
        top_reviews = reviews.filter(is_featured=True)[:3]
        
        # Prepare context
        context = {
            'product': product,
            'average_rating': average_rating,
            'review_count': review_count,
            'rating_distribution': rating_distribution,
            'top_reviews': top_reviews
        }
        
        # Cache for 30 minutes
        cache.set(cache_key, context, 60 * 30)
    else:
        context = cached_data
    
    return render(request, 'store/product_detail.html', context)

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

def get_cart_data(request):
    """API endpoint to get current cart data for live updates"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = Cart(request.session)
        cart_items = cart.get_items()
        cart_total = cart.get_total_price()
        
        # Prepare cart items data
        items_data = []
        for item in cart_items:
            items_data.append({
                'product_id': item['product'].id,
                'product_name': item['product'].name,
                'product_price': str(item['product'].price),
                'quantity': item['quantity'],
                'total_price': str(item['total_price'])
            })
        
        # Prepare response data
        response_data = {
            'cart_items': items_data,
            'cart_total': str(cart_total),
            'cart_count': len(cart_items)
        }
        
        # Add discount information if applicable
        if 'discount_amount' in request.session:
            response_data['discount_amount'] = request.session['discount_amount']
            if 'cart_total_with_discount' in request.session:
                response_data['cart_total_with_discount'] = request.session['cart_total_with_discount']
        
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'Invalid request'})

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
            # Calculate updated cart totals
            cart_items = cart.get_items()
            cart_total = cart.get_total_price()
            
            # Update session cart total
            request.session['cart_total'] = str(cart_total)
            
            # Prepare response data
            response_data = {
                'success': True, 
                'message': 'تمت إضافة المنتج إلى السلة بنجاح!',
                'cart_total': str(cart_total),
                'cart_count': cart.get_total_quantity()
            }
            
            # Apply coupon discount if applicable
            if 'coupon_id' in request.session:
                try:
                    from django.apps import apps
                    from decimal import Decimal
                    from django.utils import timezone
                    
                    Coupon = apps.get_model('store', 'Coupon')
                    coupon = Coupon.objects.get(
                        id=request.session['coupon_id'],
                        active=True,
                        valid_from__lte=timezone.now(),
                        valid_to__gte=timezone.now()
                    )
                    
                    # Calculate discount
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
                    
                    # Add discount information to response
                    response_data['discount_amount'] = str(discount_amount)
                    response_data['cart_total_with_discount'] = str(new_total)
                except Exception:
                    # If coupon is invalid, remove it from session
                    if 'coupon_id' in request.session:
                        del request.session['coupon_id']
                    if 'discount_amount' in request.session:
                        del request.session['discount_amount']
                    if 'cart_total_with_discount' in request.session:
                        del request.session['cart_total_with_discount']
            
            return JsonResponse(response_data)
    
    return redirect('view_cart')

def remove_from_cart(request, product_id):
    """Remove product from cart"""
    if request.method == 'POST':
        # Use Cart class to remove product
        cart = Cart(request.session)
        cart.remove(product_id)
        
        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Calculate updated cart totals
            cart_items = cart.get_items()
            cart_total = cart.get_total_price()
            
            # Update session cart total
            request.session['cart_total'] = str(cart_total)
            
            # Prepare response data
            response_data = {
                'success': True, 
                'message': 'تمت إزالة المنتج من السلة بنجاح!',
                'cart_total': str(cart_total),
                'cart_count': cart.get_total_quantity()
            }
            
            # Add discount information if applicable
            if 'discount_amount' in request.session:
                response_data['discount_amount'] = request.session['discount_amount']
                if 'cart_total_with_discount' in request.session:
                    response_data['cart_total_with_discount'] = request.session['cart_total_with_discount']
            
            return JsonResponse(response_data)
    
    return redirect('view_cart')

def update_cart(request, product_id):
    """Update cart item"""
    if request.method == 'POST':
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Get quantity from JSON data
            try:
                data = json.loads(request.body)
                quantity = int(data.get('quantity', 1))
            except (json.JSONDecodeError, ValueError, TypeError):
                quantity = 1
        else:
            # Get quantity from form data
            quantity = int(request.POST.get('quantity', 1))
        
        # Use Cart class to update product quantity
        cart = Cart(request.session)
        cart.update(product_id, quantity)
        
        # Return appropriate response based on request type
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Calculate updated cart totals
            cart_items = cart.get_items()
            cart_total = cart.get_total_price()
            
            # Update session cart total
            request.session['cart_total'] = str(cart_total)
            
            # Find the updated item to get its new total
            item_total = 0
            for item in cart_items:
                if str(item['product'].id) == str(product_id):
                    item_total = item['total_price']
                    break
            
            # Prepare response data
            response_data = {
                'success': True, 
                'message': 'تم تحديث السلة بنجاح!',
                'cart_total': str(cart_total),
                'item_total': str(item_total),
                'cart_count': cart.get_total_quantity()
            }
            
            # Apply coupon discount if applicable
            if 'coupon_id' in request.session:
                try:
                    from django.apps import apps
                    from decimal import Decimal
                    from django.utils import timezone
                    
                    Coupon = apps.get_model('store', 'Coupon')
                    coupon = Coupon.objects.get(
                        id=request.session['coupon_id'],
                        active=True,
                        valid_from__lte=timezone.now(),
                        valid_to__gte=timezone.now()
                    )
                    
                    # Calculate discount
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
                    
                    # Add discount information to response
                    response_data['discount_amount'] = str(discount_amount)
                    response_data['cart_total_with_discount'] = str(new_total)
                except Exception:
                    # If coupon is invalid, remove it from session
                    if 'coupon_id' in request.session:
                        del request.session['coupon_id']
                    if 'discount_amount' in request.session:
                        del request.session['discount_amount']
                    if 'cart_total_with_discount' in request.session:
                        del request.session['cart_total_with_discount']
            
            return JsonResponse(response_data)
        else:
            # Redirect for regular form submissions
            messages.success(request, 'تم تحديث السلة بنجاح!')
            return redirect('view_cart')
    
    return redirect('view_cart')

def create_order(request):
    """Create order with coupon and loyalty support"""
    if request.method == 'POST':
        try:
            from decimal import Decimal
            from django.apps import apps
            from django.utils import timezone
            
            # Import coupon utilities with error handling
            try:
                from .utils.coupon_utils import (
                    apply_coupon_to_order, 
                    calculate_earned_points, 
                    update_user_loyalty_points
                )
                coupon_utils_available = True
            except ImportError:
                coupon_utils_available = False
                logger.warning("Coupon utilities not available in create_order")
            
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
            
            # Apply coupon if present and utilities are available
            if 'coupon_id' in request.session and coupon_utils_available:
                try:
                    Coupon = apps.get_model('store', 'Coupon')
                    coupon = Coupon.objects.get(id=request.session['coupon_id'])
                    # Create temporary order for discount calculation
                    Order = apps.get_model('store', 'Order')
                    temp_order = Order(total_amount=subtotal)
                    coupon_discount = apply_coupon_to_order(temp_order, coupon.code)
                except Exception as e:
                    logger.warning(f"Error applying coupon in create_order: {str(e)}")
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
            
            # Track if we have any valid items
            has_valid_items = False
            
            for item in cart_items:
                try:
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
                    has_valid_items = True
                except Exception as e:
                    logger.error(f"Error creating order item: {str(e)}")
                    # Continue with other items even if one fails
                    pass
            
            # If no valid items were created, delete the order and show error
            if not has_valid_items:
                order.delete()
                messages.error(request, 'حدث خطأ أثناء إنشاء عناصر الطلب')
                return redirect('checkout')
            
            # Apply coupon usage if utilities are available
            if 'coupon_id' in request.session and coupon_utils_available:
                try:
                    Coupon = apps.get_model('store', 'Coupon')
                    coupon = Coupon.objects.get(id=request.session['coupon_id'])
                    coupon.times_used += 1
                    coupon.save()
                except Exception as e:
                    logger.warning(f"Error updating coupon usage: {str(e)}")
                    pass  # Invalid coupon
            
            # Calculate and award loyalty points if user is authenticated and utilities are available
            if request.user.is_authenticated and coupon_utils_available:
                try:
                    points_earned = calculate_earned_points(order, request.user)
                    update_user_loyalty_points(request.user, points_earned)
                except Exception as e:
                    logger.warning(f"Error calculating/awarding loyalty points: {str(e)}")
                    pass  # Error with loyalty points
                
                # Deduct reward points if any rewards were used
                if 'rewards' in request.session:
                    try:
                        LoyaltyProgram = apps.get_model('store', 'LoyaltyProgram')
                        loyalty_program = LoyaltyProgram.objects.get(user=request.user)
                        for reward_data in request.session['rewards']:
                            loyalty_program.points -= reward_data.get('points_required', 0)
                        if loyalty_program.points < 0:
                            loyalty_program.points = 0
                        loyalty_program.save()
                    except Exception as e:
                        logger.warning(f"Error deducting reward points: {str(e)}")
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
            logger.error(f"Error creating order: {str(e)}", exc_info=True)
            messages.error(request, 'حدث خطأ أثناء إنشاء الطلب. يرجى المحاولة مرة أخرى.')
            return redirect('checkout')
    
    return redirect('checkout')

def checkout(request):
    """Checkout view with coupon and loyalty support"""
    try:
        from decimal import Decimal
        from django.apps import apps
        
        # Import coupon utilities
        try:
            from .utils.coupon_utils import (
                apply_coupon_to_order, 
                calculate_loyalty_discount, 
                get_user_rewards,
                calculate_earned_points,
                update_user_loyalty_points
            )
            coupon_utils_available = True
        except ImportError:
            coupon_utils_available = False
            logger.warning("Coupon utilities not available")
        
        # Get cart data
        cart = Cart(request.session)
        cart_items = cart.get_items()
        subtotal = cart.get_total_price()
        
        # Initialize discount values
        coupon_discount = Decimal('0.00')
        loyalty_discount = Decimal('0.00')
        rewards_discount = Decimal('0.00')
        
        # Apply coupon if present in session and utilities are available
        if 'coupon_id' in request.session and coupon_utils_available:
            try:
                Coupon = apps.get_model('store', 'Coupon')
                coupon = Coupon.objects.get(id=request.session['coupon_id'])
                # Create a temporary order object for discount calculation
                Order = apps.get_model('store', 'Order')
                temp_order = Order(total_amount=subtotal)
                coupon_discount = apply_coupon_to_order(temp_order, coupon.code)
            except Exception as e:
                logger.warning(f"Error applying coupon in checkout: {str(e)}")
                pass  # Invalid coupon, ignore
        
        # Apply loyalty discount if user is authenticated and utilities are available
        if request.user.is_authenticated and coupon_utils_available:
            try:
                # Create a temporary order object for discount calculation
                Order = apps.get_model('store', 'Order')
                temp_order = Order(total_amount=subtotal)
                loyalty_discount = calculate_loyalty_discount(temp_order, request.user)
            except Exception as e:
                logger.warning(f"Error calculating loyalty discount: {str(e)}")
                pass  # Error calculating loyalty discount
        
        # Apply rewards discount if any rewards were selected and utilities are available
        if 'rewards' in request.session and coupon_utils_available:
            try:
                for reward_data in request.session['rewards']:
                    if reward_data.get('type') == 'discount' and reward_data.get('discount_percentage'):
                        reward_discount = (subtotal * Decimal(reward_data['discount_percentage']) / 100).quantize(Decimal('0.01'))
                        rewards_discount += reward_discount
            except Exception as e:
                logger.warning(f"Error applying rewards discount: {str(e)}")
                pass  # Error applying rewards discount
        
        # Calculate final total
        total_discount = coupon_discount + loyalty_discount + rewards_discount
        final_total = max(subtotal - total_discount, Decimal('0.00'))
        
        # Get available rewards if user is authenticated and utilities are available
        available_rewards = []
        if request.user.is_authenticated and coupon_utils_available:
            try:
                available_rewards = get_user_rewards(request.user)
            except Exception as e:
                logger.warning(f"Error getting user rewards: {str(e)}")
                pass  # Error getting user rewards
        
        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'coupon_discount': coupon_discount,
            'loyalty_discount': loyalty_discount,
            'rewards_discount': rewards_discount,
            'total_discount': total_discount,
            'final_total': final_total,
            'available_rewards': available_rewards
        }
        
        return render(request, 'store/checkout_with_discounts.html', context)
        
    except Exception as e:
        logger.error(f"Error in checkout view: {str(e)}", exc_info=True)
        return render(request, 'store/checkout_with_discounts.html', {
            'error': 'حدث خطأ أثناء تحميل صفحة الدفع. يرجى المحاولة مرة أخرى.'
        })

def order_detail(request, order_id):
    """Order detail view"""
    return render(request, 'store/order_detail.html')

def order_history(request):
    """Order history view"""
    # TODO: Implement actual order history functionality
    Order = apps.get_model('store', 'Order')
    if hasattr(request, 'user') and request.user.is_authenticated:
        # Use select_related to avoid N+1 query issues
        orders = Order.objects.filter(user=request.user).select_related('user').prefetch_related('items__product')
        return render(request, 'store/order_history.html', {'orders': orders})
    else:
        messages.error(request, "يجب تسجيل الدخول لعرض تاريخ الطلبات")
        return redirect('home')

def notifications(request):
    """Notifications view"""
    # TODO: Implement actual notifications functionality
    Notification = apps.get_model('store', 'Notification')
    if hasattr(request, 'user') and request.user.is_authenticated:
        # Use select_related to avoid N+1 query issues
        notifications = Notification.objects.filter(user=request.user).select_related('user', 'order')
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
    from django.apps import apps
    Product = apps.get_model('store', 'Product')
    Order = apps.get_model('store', 'Order')
    SocialMediaIntegration = apps.get_model('store', 'SocialMediaIntegration')
    ShippingIntegration = apps.get_model('store', 'ShippingIntegration')
    ExternalInventory = apps.get_model('store', 'ExternalInventory')
    AnalyticsIntegration = apps.get_model('store', 'AnalyticsIntegration')
    
    # Get statistics
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    
    # Get integration data
    social_media_integrations = SocialMediaIntegration.objects.select_related('product').all()[:10]
    shipping_integrations = ShippingIntegration.objects.select_related('order').all()[:10]
    external_inventories = ExternalInventory.objects.select_related('product').all()[:10]
    analytics_events = AnalyticsIntegration.objects.select_related('user', 'product', 'order').all()[:10]
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'social_media_integrations': social_media_integrations,
        'shipping_integrations': shipping_integrations,
        'external_inventories': external_inventories,
        'analytics_events': analytics_events,
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
                SUM(oi.quantity) as total_sales
            FROM store_order o
            JOIN store_orderitem oi ON o.id = oi.order_id
            WHERE o.created_at >= DATE_TRUNC('year', CURRENT_DATE)
            GROUP BY EXTRACT(month FROM o.created_at)
            ORDER BY month
        """)
        monthly_sales_data = cursor.fetchall()
    
    # TODO: Implement actual order history functionality
    Order = apps.get_model('store', 'Order')
    return render(request, 'store/seller_dashboard.html', {
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_commissions': total_commissions,
        'total_commission_amount': total_commission_amount,
        'recent_commissions': recent_commissions,
        'monthly_sales_data': monthly_sales_data
    })


@login_required
def seller_payout_requests(request):
    """View seller payout requests"""
    # Check if user has seller profile
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'seller':
            messages.error(request, 'ليس لديك صلاحية الوصول إلى طلبات السحب')
            return redirect('home')
    except:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى طلبات السحب')
        return redirect('home')
    
    # Import model
    from django.apps import apps
    from django.db.models import Sum
    WithdrawalRequest = apps.get_model('store', 'WithdrawalRequest')
    Commission = apps.get_model('store', 'Commission')
    
    # Get seller's withdrawal requests
    withdrawal_requests = WithdrawalRequest.objects.filter(seller=request.user).order_by('-created_at')
    
    # Calculate available balance
    seller_commissions = Commission.objects.filter(user=request.user, is_paid=False)
    available_balance = seller_commissions.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    context = {
        'withdrawal_requests': withdrawal_requests,
        'available_balance': available_balance
    }
    
    return render(request, 'store/seller_payout_requests.html', context)


@login_required
def create_payout_request(request):
    """Create a new payout request"""
    # Check if user has seller profile
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'seller':
            messages.error(request, 'ليس لديك صلاحية إنشاء طلبات سحب')
            return redirect('home')
    except:
        messages.error(request, 'ليس لديك صلاحية إنشاء طلبات سحب')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            # Import models
            from django.apps import apps
            from decimal import Decimal
            WithdrawalRequest = apps.get_model('store', 'WithdrawalRequest')
            Commission = apps.get_model('store', 'Commission')
            
            # Get form data
            amount = request.POST.get('amount')
            payment_method = request.POST.get('payment_method')
            bank_name = request.POST.get('bank_name', '')
            bank_account_number = request.POST.get('bank_account_number', '')
            iban = request.POST.get('iban', '')
            paypal_email = request.POST.get('paypal_email', '')
            notes = request.POST.get('notes', '')
            
            # Validate amount
            try:
                amount_decimal = Decimal(amount)
                if amount_decimal <= 0:
                    messages.error(request, 'المبلغ يجب أن يكون أكبر من صفر')
                    return redirect('seller_payout_requests')
            except (ValueError, TypeError):
                messages.error(request, 'المبلغ غير صحيح')
                return redirect('seller_payout_requests')
            
            # Check if seller has enough commission balance
            seller_commissions = Commission.objects.filter(user=request.user, is_paid=False)
            total_earned = seller_commissions.aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')
            
            if amount_decimal > total_earned:
                messages.error(request, f'لا يمكنك سحب مبلغ أكبر من رصيدك المتاح ({total_earned})')
                return redirect('seller_payout_requests')
            
            # Create withdrawal request
            withdrawal_request = WithdrawalRequest.objects.create(
                seller=request.user,
                amount=amount_decimal,
                currency='USD',  # Default currency
                payment_method=payment_method,
                bank_name=bank_name if payment_method == 'bank_transfer' else None,
                bank_account_number=bank_account_number if payment_method == 'bank_transfer' else None,
                iban=iban if payment_method == 'bank_transfer' else None,
                paypal_email=paypal_email if payment_method == 'paypal' else None,
                notes=notes
            )
            
            messages.success(request, 'تم إنشاء طلب السحب بنجاح')
            return redirect('seller_payout_requests')
            
        except Exception as e:
            logger.error(f"Error creating payout request: {str(e)}")
            messages.error(request, 'حدث خطأ أثناء إنشاء طلب السحب')
            return redirect('seller_payout_requests')
    
    return redirect('seller_payout_requests')


@login_required
def manager_payout_requests(request):
    """View all payout requests (manager only)"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى طلبات السحب')
        return redirect('home')
    
    # Import model
    from django.apps import apps
    WithdrawalRequest = apps.get_model('store', 'WithdrawalRequest')
    
    # Get all withdrawal requests
    withdrawal_requests = WithdrawalRequest.objects.all().order_by('-created_at')
    
    context = {
        'withdrawal_requests': withdrawal_requests
    }
    
    return render(request, 'store/manager_payout_requests.html', context)


@login_required
def update_payout_request_status(request, request_id):
    """Update payout request status (manager only)"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية تحديث حالة طلبات السحب')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            # Import model
            from django.apps import apps
            from django.utils import timezone
            WithdrawalRequest = apps.get_model('store', 'WithdrawalRequest')
            
            # Get the withdrawal request
            withdrawal_request = get_object_or_404(WithdrawalRequest, id=request_id)
            
            # Get new status
            new_status = request.POST.get('status')
            
            # Validate status
            if new_status not in dict(WithdrawalRequest.STATUS_CHOICES):
                messages.error(request, 'حالة غير صحيحة')
                return redirect('manager_payout_requests')
            
            # Update status
            old_status = withdrawal_request.status
            withdrawal_request.status = new_status
            
            # Set timestamps based on status
            if new_status == 'processing' and old_status != 'processing':
                withdrawal_request.processed_at = timezone.now()
            elif new_status == 'completed' and old_status != 'completed':
                withdrawal_request.completed_at = timezone.now()
            
            withdrawal_request.save()
            
            # Add notification for seller
            Notification = apps.get_model('store', 'Notification')
            Notification.objects.create(
                user=withdrawal_request.seller,
                notification_type='payout_status_changed',
                message=f'تم تحديث حالة طلب السحب #{withdrawal_request.id} إلى {withdrawal_request.get_status_display_arabic()}',
                order=None
            )
            
            messages.success(request, 'تم تحديث حالة طلب السحب بنجاح')
            
        except Exception as e:
            logger.error(f"Error updating payout request status: {str(e)}")
            messages.error(request, 'حدث خطأ أثناء تحديث حالة طلب السحب')
    
    return redirect('manager_payout_requests')

    if hasattr(request, 'user') and request.user.is_authenticated:
        # Use select_related to avoid N+1 query issues
        orders = Order.objects.filter(user=request.user).select_related('user').prefetch_related('items__product')
        return render(request, 'store/order_history.html', {'orders': orders})
    else:
        messages.error(request, "يجب تسجيل الدخول لعرض تاريخ الطلبات")
        return redirect('home')

def notifications(request):
    """Notifications view"""
    # TODO: Implement actual notifications functionality
    Notification = apps.get_model('store', 'Notification')
    if hasattr(request, 'user') and request.user.is_authenticated:
        # Use select_related to avoid N+1 query issues
        notifications = Notification.objects.filter(user=request.user).select_related('user', 'order')
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
    """Optimize images view - performs actual image optimization when POST request is made"""
    if request.method == 'POST':
        try:
            from store.utils import optimize_product_images
            optimize_product_images()
            messages.success(request, 'تم تحسين جميع صور المنتجات بنجاح!')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء تحسين الصور: {str(e)}')
    
    return render(request, 'store/optimize_images.html')

def signup(request):
    """Signup view"""
    return render(request, 'store/signup.html')

@login_required
def manager_dashboard(request):
    """Manager dashboard view with caching"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى لوحة تحكم المدير')
        return redirect('home')
    
    # Try to get manager dashboard data from cache first
    cache_key = f'manager_dashboard_data_{request.user.id}'
    dashboard_data = cache.get(cache_key)
    
    if dashboard_data is None:
        # Import models
        from django.apps import apps
        Product = apps.get_model('store', 'Product')
        Order = apps.get_model('store', 'Order')
        SocialMediaIntegration = apps.get_model('store', 'SocialMediaIntegration')
        ShippingIntegration = apps.get_model('store', 'ShippingIntegration')
        ExternalInventory = apps.get_model('store', 'ExternalInventory')
        AnalyticsIntegration = apps.get_model('store', 'AnalyticsIntegration')
        
        # Get statistics
        total_products = Product.objects.count()
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        
        # Get integration data
        social_media_integrations = SocialMediaIntegration.objects.select_related('product').all()[:10]
        shipping_integrations = ShippingIntegration.objects.select_related('order').all()[:10]
        external_inventories = ExternalInventory.objects.select_related('product').all()[:10]
        analytics_events = AnalyticsIntegration.objects.select_related('user', 'product', 'order').all()[:20]
        
        dashboard_data = {
            'total_products': total_products,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'social_media_integrations': social_media_integrations,
            'shipping_integrations': shipping_integrations,
            'external_inventories': external_inventories,
            'analytics_events': analytics_events,
        }
        
        # Cache for 5 minutes (since this data changes frequently)
        cache.set(cache_key, dashboard_data, 60 * 5)
    
    return render(request, 'store/manager_dashboard.html', dashboard_data)

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
                SUM(oi.quantity) as total_sales
            FROM store_order o
            JOIN store_orderitem oi ON o.id = oi.order_id
            WHERE o.created_at >= DATE_TRUNC('year', CURRENT_DATE)
            GROUP BY EXTRACT(month FROM o.created_at)
            ORDER BY month
        """)
        monthly_sales_data = cursor.fetchall()
    
    # TODO: Implement actual order history functionality
    Order = apps.get_model('store', 'Order')
    if hasattr(request, 'user') and request.user.is_authenticated:
        # Use select_related to avoid N+1 query issues
        orders = Order.objects.filter(user=request.user).select_related('user').prefetch_related('items__product')
        return render(request, 'store/order_history.html', {'orders': orders})
    else:
        messages.error(request, "يجب تسجيل الدخول لعرض تاريخ الطلبات")
        return redirect('home')

def notifications(request):
    """Notifications view"""
    # TODO: Implement actual notifications functionality
    Notification = apps.get_model('store', 'Notification')
    if hasattr(request, 'user') and request.user.is_authenticated:
        # Use select_related to avoid N+1 query issues
        notifications = Notification.objects.filter(user=request.user).select_related('user', 'order')
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
    """Manager dashboard view with caching and integration data"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى لوحة تحكم المدير')
        return redirect('home')
    
    # Try to get manager dashboard data from cache first
    cache_key = cache_service.get_dashboard_statistics_cache_key(request.user.id)
    dashboard_data = cache_service.get_or_set(
        cache_key,
        lambda: None,  # Will be computed below if None
        cache_service.MEDIUM_TIMEOUT
    )
    
    if dashboard_data is None:
        # Import models
        from django.apps import apps
        from django.db.models import Sum, Count, Q, Prefetch
        Product = apps.get_model('store', 'Product')
        Order = apps.get_model('store', 'Order')
        UserProfile = apps.get_model('store', 'UserProfile')
        Commission = apps.get_model('store', 'Commission')
        SocialMediaIntegration = apps.get_model('store', 'SocialMediaIntegration')
        ShippingIntegration = apps.get_model('store', 'ShippingIntegration')
        ExternalInventory = apps.get_model('store', 'ExternalInventory')
        AnalyticsIntegration = apps.get_model('store', 'AnalyticsIntegration')
        OrderItem = apps.get_model('store', 'OrderItem')
        
        # Get enhanced statistics with optimized queries
        total_products = Product.objects.count()
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        
        # New requested statistics
        total_sellers = UserProfile.objects.filter(role='seller').count()
        
        # Calculate total profits from commissions
        total_profits = Commission.objects.aggregate(total=Sum('amount'))['total'] or 0
        
        # Get pending/rejected products
        pending_products = Product.objects.filter(verification_status='pending').count()
        rejected_products = Product.objects.filter(verification_status='rejected').count()
        
        # Get integration data with optimized queries
        social_media_integrations = SocialMediaIntegration.objects.select_related(
            'product', 'product__seller'
        ).prefetch_related(
            'product__orderitem_set'
        ).all()[:10]
        
        shipping_integrations = ShippingIntegration.objects.select_related(
            'order', 'order__user'
        ).prefetch_related(
            'order__items', 'order__items__product'
        ).all()[:10]
        
        external_inventories = ExternalInventory.objects.select_related(
            'product', 'product__seller'
        ).all()[:10]
        
        analytics_events = AnalyticsIntegration.objects.select_related(
            'user', 'product', 'product__seller', 'order', 'order__user'
        ).prefetch_related(
            'product__orderitem_set', 'order__items', 'order__items__product'
        ).all()[:20]
        
        # Get recent orders with optimized queries
        recent_orders = Order.objects.select_related(
            'user'
        ).prefetch_related(
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related('product', 'product__seller')
            )
        ).order_by('-created_at')[:10]
        
        dashboard_data = {
            'total_products': total_products,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_sellers': total_sellers,
            'total_profits': total_profits,
            'pending_products': pending_products,
            'rejected_products': rejected_products,
            'social_media_integrations': social_media_integrations,
            'shipping_integrations': shipping_integrations,
            'external_inventories': external_inventories,
            'analytics_events': analytics_events,
            'recent_orders': recent_orders,
        }
        
        # Cache for 5 minutes (since this data changes frequently)
        cache.set(cache_key, dashboard_data, cache_service.SHORT_TIMEOUT)
    
    return render(request, 'store/manager_dashboard.html', dashboard_data)


@login_required
def manager_user_search(request):
    """Manager user search view with optimized queries"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى البحث عن المستخدمين')
        return redirect('home')
    
    # Import models
    from django.apps import apps
    from django.db.models import Q, Prefetch
    from django.core.paginator import Paginator
    from django.contrib.auth.models import Group
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('store', 'UserProfile')
    Order = apps.get_model('store', 'Order')
    
    # Get search query
    query = request.GET.get('q', '')
    
    # Start with all users with optimized queries
    users = User.objects.all().select_related(
        'userprofile'
    ).prefetch_related(
        Prefetch(
            'groups',
            queryset=Group.objects.only('name')
        ),
        Prefetch(
            'order_set',
            queryset=Order.objects.only('id', 'status', 'total_amount', 'created_at')
        )
    ).order_by('-date_joined')
    
    # Apply search query
    if query:
        users = users.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(userprofile__phone_number__icontains=query)
        )
    
    # Paginate results
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'search_query': query,
    }
    
    return render(request, 'store/manager_user_search.html', context)


@login_required
def manager_manage_permissions(request):
    """Manager permission management view with optimized queries"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى إدارة الصلاحيات')
        return redirect('home')
    
    # Import models
    from django.apps import apps
    from django.db.models import Q, Prefetch
    from django.core.paginator import Paginator
    from django.contrib.auth.models import Group, Permission
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('store', 'UserProfile')
    Order = apps.get_model('store', 'Order')
    
    # Handle form submission for permission changes
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role = request.POST.get('role')
        
        try:
            # Get user with optimized query
            user = User.objects.select_related('userprofile').prefetch_related(
                Prefetch(
                    'order_set',
                    queryset=Order.objects.only('id', 'status', 'total_amount')
                )
            ).get(id=user_id)
            
            # Update user role
            if hasattr(user, 'userprofile'):
                user.userprofile.role = role
                user.userprofile.save()
            else:
                UserProfile.objects.create(user=user, role=role)
            
            messages.success(request, f'تم تحديث دور المستخدم {user.username} بنجاح')
        except User.DoesNotExist:
            messages.error(request, 'المستخدم غير موجود')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء تحديث الدور: {str(e)}')
        
        return redirect('manager_manage_permissions')
    
    # Get all users with pagination and optimized queries
    users = User.objects.all().select_related(
        'userprofile'
    ).prefetch_related(
        Prefetch(
            'groups',
            queryset=Group.objects.only('name')
        ),
        Prefetch(
            'order_set',
            queryset=Order.objects.only('id', 'status', 'total_amount', 'created_at')
        )
    ).order_by('-date_joined')
    
    # Paginate results
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get available roles
    roles = UserProfile.USER_ROLES
    
    context = {
        'users': page_obj,
        'roles': roles,
    }
    
    return render(request, 'store/manager_permissions.html', context)

@login_required
def buyer_dashboard(request):
    """Buyer dashboard view with caching and optimized queries"""
    # Check if user has buyer profile
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'buyer':
            messages.error(request, 'ليس لديك صلاحية الوصول إلى لوحة تحكم المشتري')
            return redirect('home')
    except:
        # If no profile, assume it's a buyer
        pass
    
    # Try to get buyer dashboard data from cache first
    cache_key = cache_service.get_dashboard_statistics_cache_key(request.user.id)
    dashboard_data = cache_service.get_or_set(
        cache_key,
        lambda: None,  # Will be computed below if None
        cache_service.MEDIUM_TIMEOUT
    )
    
    if dashboard_data is None:
        # Import models
        from django.db.models import Prefetch
        Order = apps.get_model('store', 'Order')
        OrderItem = apps.get_model('store', 'OrderItem')
        
        # Get buyer-specific statistics with optimized queries
        user_orders = Order.objects.filter(user=request.user).select_related(
            'user'
        ).prefetch_related(
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related('product', 'product__seller')
            )
        )
        
        total_orders = user_orders.count()
        pending_orders = user_orders.filter(status='pending').count()
        
        # Get recent orders with optimized queries
        recent_orders = user_orders.order_by('-created_at')[:5]
        
        dashboard_data = {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'recent_orders': recent_orders,
        }
        
        # Cache for 5 minutes (since this data changes frequently)
        cache.set(cache_key, dashboard_data, cache_service.SHORT_TIMEOUT)
    
    return render(request, 'store/buyer_dashboard.html', dashboard_data)

@login_required
def seller_dashboard(request):
    """Seller dashboard view with caching and optimized queries"""
    # Check if user has seller profile
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'seller':
            messages.error(request, 'ليس لديك صلاحية الوصول إلى لوحة تحكم البائع')
            return redirect('home')
    except:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى لوحة تحكم البائع')
        return redirect('home')
    
    # Try to get seller dashboard data from cache first
    cache_key = cache_service.get_dashboard_statistics_cache_key(request.user.id)
    dashboard_data = cache_service.get_or_set(
        cache_key,
        lambda: None,  # Will be computed below if None
        cache_service.MEDIUM_TIMEOUT
    )
    
    if dashboard_data is None:
        # Import models
        from django.db.models import Prefetch
        Product = apps.get_model('store', 'Product')
        Order = apps.get_model('store', 'Order')
        OrderItem = apps.get_model('store', 'OrderItem')
        Commission = apps.get_model('store', 'Commission')
        
        # Get seller-specific statistics with optimized queries
        seller_products = Product.objects.filter(seller=request.user).select_related(
            'seller'
        )
        total_products = seller_products.count()
        
        # Get orders for seller's products with optimized queries
        seller_orders = Order.objects.filter(
            items__product__seller=request.user
        ).distinct().select_related(
            'user'
        ).prefetch_related(
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related('product', 'product__seller')
            )
        )
        total_orders = seller_orders.count()
        pending_orders = seller_orders.filter(status='pending').count()
        
        # Get commission data with optimized queries
        seller_commissions = Commission.objects.filter(user=request.user).select_related(
            'user', 'order'
        )
        total_commissions = seller_commissions.count()
        total_commission_amount = seller_commissions.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Get recent commissions with optimized queries
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
        
        # Top selling products with optimized queries
        top_products = Product.objects.filter(seller=request.user).select_related(
            'seller'
        ).annotate(
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
        
        dashboard_data = {
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
        
        # Cache for 5 minutes (since this data changes frequently)
        cache.set(cache_key, dashboard_data, cache_service.SHORT_TIMEOUT)
    
    # Render the luxury dashboard template
    return render(request, 'store/seller_dashboard_luxury.html', dashboard_data)

@login_required
def buyer_dashboard(request):
    """Buyer dashboard view with caching and optimized queries"""
    # Check if user has buyer profile
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'buyer':
            messages.error(request, 'ليس لديك صلاحية الوصول إلى لوحة تحكم المشتري')
            return redirect('home')
    except:
        # If no profile, assume it's a buyer
        pass
    
    # Try to get buyer dashboard data from cache first
    cache_key = cache_service.get_dashboard_statistics_cache_key(request.user.id)
    dashboard_data = cache_service.get_or_set(
        cache_key,
        lambda: None,  # Will be computed below if None
        cache_service.MEDIUM_TIMEOUT
    )
    
    if dashboard_data is None:
        # Import models
        from django.db.models import Prefetch
        Order = apps.get_model('store', 'Order')
        OrderItem = apps.get_model('store', 'OrderItem')
        
        # Get buyer-specific statistics with optimized queries
        user_orders = Order.objects.filter(user=request.user).select_related(
            'user'
        ).prefetch_related(
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related('product', 'product__seller')
            )
        )
        
        total_orders = user_orders.count()
        pending_orders = user_orders.filter(status='pending').count()
        
        # Get recent orders with optimized queries
        recent_orders = user_orders.order_by('-created_at')[:5]
        
        dashboard_data = {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'recent_orders': recent_orders,
        }
        
        # Cache for 5 minutes (since this data changes frequently)
        cache.set(cache_key, dashboard_data, cache_service.SHORT_TIMEOUT)
    
    return render(request, 'store/buyer_dashboard.html', dashboard_data)

def seller_products(request):
    """Seller products view"""
    return render(request, 'store/seller_products.html')

@login_required
def add_product(request):
    """Add product view with form handling"""
    # Check if user has seller profile
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'seller':
            messages.error(request, 'ليس لديك صلاحية إضافة منتجات')
            return redirect('home')
    except:
        messages.error(request, 'ليس لديك صلاحية إضافة منتجات')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            # Import model
            from django.apps import apps
            Product = apps.get_model('store', 'Product')
            
            # Get form data
            name = request.POST.get('name')
            price = request.POST.get('price')
            category = request.POST.get('category', 'phones')
            description = request.POST.get('description', '')
            
            # Validate required fields
            if not name or not price:
                messages.error(request, 'يرجى ملء جميع الحقول المطلوبة')
                return render(request, 'store/add_product.html')
            
            # Validate price
            try:
                price_decimal = Decimal(price)
                if price_decimal <= 0:
                    messages.error(request, 'السعر يجب أن يكون أكبر من صفر')
                    return render(request, 'store/add_product.html')
            except (ValueError, TypeError):
                messages.error(request, 'السعر غير صحيح')
                return render(request, 'store/add_product.html')
            
            # Create product
            product = Product.objects.create(
                name=name,
                price=price_decimal,
                category=category,
                description=description,
                seller=request.user
            )
            
            # Handle image upload
            if request.FILES.get('image'):
                product.image = request.FILES['image']
                product.save()
            
            messages.success(request, 'تمت إضافة المنتج بنجاح')
            return redirect('seller_products')
            
        except Exception as e:
            logger.error(f"Error adding product: {str(e)}")
            messages.error(request, 'حدث خطأ أثناء إضافة المنتج')
            return render(request, 'store/add_product.html')
    
    return render(request, 'store/add_product.html')

@login_required
def edit_product(request, product_id):
    """Edit product view with form handling"""
    # Check if user has seller profile
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'seller':
            messages.error(request, 'ليس لديك صلاحية تعديل المنتجات')
            return redirect('home')
    except:
        messages.error(request, 'ليس لديك صلاحية تعديل المنتجات')
        return redirect('home')
    
    # Import model
    from django.apps import apps
    Product = apps.get_model('store', 'Product')
    
    # Get product
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            price = request.POST.get('price')
            category = request.POST.get('category', 'phones')
            description = request.POST.get('description', '')
            
            # Validate required fields
            if not name or not price:
                messages.error(request, 'يرجى ملء جميع الحقول المطلوبة')
                return render(request, 'store/edit_product.html', {'product': product})
            
            # Validate price
            try:
                price_decimal = Decimal(price)
                if price_decimal <= 0:
                    messages.error(request, 'السعر يجب أن يكون أكبر من صفر')
                    return render(request, 'store/edit_product.html', {'product': product})
            except (ValueError, TypeError):
                messages.error(request, 'السعر غير صحيح')
                return render(request, 'store/edit_product.html', {'product': product})
            
            # Update product
            product.name = name
            product.price = price_decimal
            product.category = category
            product.description = description
            
            # Handle image upload
            if request.FILES.get('image'):
                product.image = request.FILES['image']
            
            product.save()
            
            messages.success(request, 'تم تحديث المنتج بنجاح')
            return redirect('seller_products')
            
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            messages.error(request, 'حدث خطأ أثناء تحديث المنتج')
            return render(request, 'store/edit_product.html', {'product': product})
    
    return render(request, 'store/edit_product.html', {'product': product})

@login_required
def delete_product(request, product_id):
    """Delete product view"""
    # Check if user has seller profile
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'seller':
            messages.error(request, 'ليس لديك صلاحية حذف المنتجات')
            return redirect('home')
    except:
        messages.error(request, 'ليس لديك صلاحية حذف المنتجات')
        return redirect('home')
    
    # Import model
    from django.apps import apps
    Product = apps.get_model('store', 'Product')
    
    # Get product
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    # Delete product
    product.delete()
    
    messages.success(request, 'تم حذف المنتج بنجاح')
    return redirect('seller_products')

@login_required
def seller_orders(request):
    """Seller orders view"""
    # Check if user has seller profile
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'seller':
            messages.error(request, 'ليس لديك صلاحية الوصول إلى طلبات البائع')
            return redirect('home')
    except:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى طلبات البائع')
        return redirect('home')
    
    # Import models
    from django.apps import apps
    Order = apps.get_model('store', 'Order')
    OrderItem = apps.get_model('store', 'OrderItem')
    
    # Get orders for seller's products
    orders = Order.objects.filter(items__product__seller=request.user).distinct().order_by('-created_at')
    
    # Annotate orders with seller items
    for order in orders:
        order.seller_items = order.items.filter(product__seller=request.user)
    
    context = {
        'orders': orders
    }
    
    return render(request, 'store/seller_orders.html', context)

@login_required
def seller_order_detail(request, order_id):
    """Seller order detail view"""
    # Check if user has seller profile
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'seller':
            messages.error(request, 'ليس لديك صلاحية الوصول إلى تفاصيل الطلب')
            return redirect('home')
    except:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى تفاصيل الطلب')
        return redirect('home')
    
    # Import models
    from django.apps import apps
    from django.shortcuts import get_object_or_404
    Order = apps.get_model('store', 'Order')
    OrderItem = apps.get_model('store', 'OrderItem')
    
    # Get order
    order = get_object_or_404(Order, id=order_id)
    
    # Check if seller has items in this order
    order_items = OrderItem.objects.filter(order=order, product__seller=request.user)
    
    if not order_items.exists():
        messages.error(request, 'ليس لديك صلاحية الوصول إلى هذا الطلب')
        return redirect('seller_orders')
    
    context = {
        'order': order,
        'order_items': order_items
    }
    
    return render(request, 'store/seller_order_detail.html', context)

@login_required
def update_order_status(request, order_id):
    """Update order status view"""
    # Check if user has seller profile
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'seller':
            messages.error(request, 'ليس لديك صلاحية تحديث حالة الطلب')
            return redirect('home')
    except:
        messages.error(request, 'ليس لديك صلاحية تحديث حالة الطلب')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            # Import models
            from django.apps import apps
            from django.shortcuts import get_object_or_404
            from django.utils import timezone
            Order = apps.get_model('store', 'Order')
            OrderItem = apps.get_model('store', 'OrderItem')
            Notification = apps.get_model('store', 'Notification')
            
            # Get order
            order = get_object_or_404(Order, id=order_id)
            
            # Check if seller has items in this order
            order_items = OrderItem.objects.filter(order=order, product__seller=request.user)
            
            if not order_items.exists():
                messages.error(request, 'ليس لديك صلاحية تحديث حالة هذا الطلب')
                return redirect('seller_orders')
            
            # Get new status
            new_status = request.POST.get('status')
            
            # Validate status
            if new_status not in dict(Order.STATUS_CHOICES):
                messages.error(request, 'حالة غير صحيحة')
                return redirect('seller_order_detail', order_id=order_id)
            
            # Additional validation for delivered status
            if new_status == 'delivered' and order.status != 'shipped':
                messages.error(request, 'لا يمكن تغيير الحالة إلى تم التسليم إلا من حالة تم الشحن')
                return redirect('seller_order_detail', order_id=order_id)
            
            # Update order status
            old_status = order.status
            order.status = new_status
            order.updated_at = timezone.now()
            order.save()
            
            # Create notification for buyer
            Notification.objects.create(
                user=order.user,
                order=order,
                notification_type='order_status_changed',
                message=f'تغيرت حالة طلبك #{order.id} إلى {order.get_status_display()}'
            )
            
            # Additional notifications for specific status changes
            if new_status == 'shipped':
                Notification.objects.create(
                    user=order.user,
                    order=order,
                    notification_type='order_shipped',
                    message=f'طلبك #{order.id} تم شحنه'
                )
            elif new_status == 'delivered':
                Notification.objects.create(
                    user=order.user,
                    order=order,
                    notification_type='order_delivered',
                    message=f'طلبك #{order.id} تم تسليمه'
                )
            
            messages.success(request, 'تم تحديث حالة الطلب بنجاح')
            
        except Exception as e:
            logger.error(f"Error updating order status: {str(e)}")
            messages.error(request, 'حدث خطأ أثناء تحديث حالة الطلب')
    
    return redirect('seller_order_detail', order_id=order_id)

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
    from django.apps import apps
    Wishlist = apps.get_model('store', 'Wishlist')
    
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
        # Calculate total value
        total_value = sum(item.product.price for item in wishlist_items)
    else:
        wishlist_items = []
        total_value = 0
    
    context = {
        'wishlist_items': wishlist_items,
        'total_value': total_value
    }
    return render(request, 'store/wishlist.html', context)

def add_to_wishlist(request, product_id):
    """Add to wishlist"""
    from django.apps import apps
    from django.contrib import messages
    from django.shortcuts import get_object_or_404, redirect
    Product = apps.get_model('store', 'Product')
    Wishlist = apps.get_model('store', 'Wishlist')
    
    if not request.user.is_authenticated:
        messages.error(request, 'يجب تسجيل الدخول لإضافة منتجات إلى قائمة المفضلة')
        return redirect('product_detail', pk=product_id)
    
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, 'تمت إضافة المنتج إلى قائمة المفضلة')
    else:
        messages.info(request, 'المنتج موجود بالفعل في قائمة المفضلة')
    
    return redirect('product_detail', pk=product_id)

def remove_from_wishlist(request, product_id):
    """Remove from wishlist"""
    from django.apps import apps
    from django.contrib import messages
    Wishlist = apps.get_model('store', 'Wishlist')
    
    if not request.user.is_authenticated:
        messages.error(request, 'يجب تسجيل الدخول لإزالة منتجات من قائمة المفضلة')
        return redirect('view_wishlist')
    
    try:
        wishlist_item = Wishlist.objects.get(
            user=request.user,
            product_id=product_id
        )
        wishlist_item.delete()
        messages.success(request, 'تمت إزالة المنتج من قائمة المفضلة')
    except Wishlist.DoesNotExist:
        messages.error(request, 'المنتج غير موجود في قائمة المفضلة')
    
    return redirect('view_wishlist')

def add_review(request, product_id):
    """Add review"""
    from django.apps import apps
    from django.contrib import messages
    from django.shortcuts import get_object_or_404
    Product = apps.get_model('store', 'Product')
    Review = apps.get_model('store', 'Review')
    
    if not request.user.is_authenticated:
        messages.error(request, 'يجب تسجيل الدخول لإضافة تقييم')
        return redirect('product_detail', pk=product_id)
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        
        if rating and comment:
            # Check if user has purchased the product
            from .models import OrderItem
            is_verified = OrderItem.objects.filter(
                order__user=request.user,
                product=product,
                order__status='delivered'
            ).exists()
            
            # Create or update review
            review, created = Review.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={
                    'rating': rating,
                    'comment': comment,
                    'is_verified_purchase': is_verified
                }
            )
            
            if not created:
                # Update existing review
                review.rating = rating
                review.comment = comment
                review.is_verified_purchase = is_verified
                review.save()
                messages.success(request, 'تم تحديث تقييمك بنجاح')
            else:
                messages.success(request, 'تم إضافة تقييمك بنجاح')
            
            return redirect('product_detail', pk=product_id)
        else:
            messages.error(request, 'يرجى ملء جميع الحقول المطلوبة')
    
    context = {
        'product': product
    }
    return render(request, 'store/add_review.html', context)

def delete_review(request, review_id):
    """Delete review"""
    from django.apps import apps
    from django.contrib import messages
    from django.shortcuts import get_object_or_404
    Review = apps.get_model('store', 'Review')
    
    if not request.user.is_authenticated:
        messages.error(request, 'يجب تسجيل الدخول لحذف التقييم')
        return redirect('product_detail', pk=request.GET.get('product_id', 1))
    
    review = get_object_or_404(Review, id=review_id)
    
    # Check if user owns the review or is staff
    if review.user == request.user or request.user.is_staff:
        product_id = review.product.id
        review.delete()
        messages.success(request, 'تم حذف التقييم بنجاح')
        return redirect('product_detail', pk=product_id)
    else:
        messages.error(request, 'ليس لديك صلاحية لحذف هذا التقييم')
        return redirect('product_detail', pk=review.product.id)

def view_comparison(request):
    """View comparison"""
    from django.apps import apps
    ProductComparison = apps.get_model('store', 'ProductComparison')
    Product = apps.get_model('store', 'Product')
    
    # Get or create comparison session
    comparison_id = request.session.get('comparison_id')
    comparison = None
    products = []
    
    if comparison_id:
        try:
            comparison = ProductComparison.objects.get(id=comparison_id)
            products = comparison.products.all()
        except ProductComparison.DoesNotExist:
            # Clear invalid session
            if 'comparison_id' in request.session:
                del request.session['comparison_id']
    
    context = {
        'products': products
    }
    return render(request, 'store/product_comparison.html', context)

def add_to_comparison(request, product_id):
    """Add to comparison"""
    from django.apps import apps
    from django.contrib import messages
    from django.shortcuts import get_object_or_404, redirect
    ProductComparison = apps.get_model('store', 'ProductComparison')
    Product = apps.get_model('store', 'Product')
    
    product = get_object_or_404(Product, id=product_id)
    
    # Get or create comparison session
    comparison_id = request.session.get('comparison_id')
    comparison = None
    
    if comparison_id:
        try:
            comparison = ProductComparison.objects.get(id=comparison_id)
        except ProductComparison.DoesNotExist:
            # Clear invalid session
            if 'comparison_id' in request.session:
                del request.session['comparison_id']
    
    if not comparison:
        # Create new comparison
        comparison = ProductComparison.objects.create()
        request.session['comparison_id'] = comparison.id
    
    # Add product to comparison (limit to 4 products)
    if comparison.products.count() >= 4:
        messages.error(request, 'يمكن مقارنة 4 منتجات كحد أقصى')
    else:
        comparison.products.add(product)
        messages.success(request, 'تمت إضافة المنتج للمقارنة')
    
    return redirect('view_comparison')

def remove_from_comparison(request, product_id):
    """Remove from comparison"""
    from django.apps import apps
    from django.contrib import messages
    ProductComparison = apps.get_model('store', 'ProductComparison')
    Product = apps.get_model('store', 'Product')
    
    comparison_id = request.session.get('comparison_id')
    if comparison_id:
        try:
            comparison = ProductComparison.objects.get(id=comparison_id)
            product = Product.objects.get(id=product_id)
            comparison.products.remove(product)
            messages.success(request, 'تمت إزالة المنتج من المقارنة')
            
            # If no products left, delete comparison and clear session
            if comparison.products.count() == 0:
                comparison.delete()
                if 'comparison_id' in request.session:
                    del request.session['comparison_id']
        except (ProductComparison.DoesNotExist, Product.DoesNotExist):
            messages.error(request, 'المنتج غير موجود في المقارنة')
    else:
        messages.error(request, 'لا توجد مقارنة نشطة')
    
    return redirect('view_comparison')

def advanced_search(request):
    """Advanced search view with faceted filtering and AI enhancements"""
    from django.apps import apps
    from django.db.models import Q, Min, Max, Avg, Count
    from decimal import Decimal
    from django.core.paginator import Paginator
    
    Product = apps.get_model('store', 'Product')
    
    # Get search parameters
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort_by', 'name')
    brand = request.GET.get('brand', '')
    rating = request.GET.get('rating', '')
    
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
    
    # Apply brand filter
    if brand:
        products = products.filter(brand__icontains=brand)
    
    # Apply price filters
    if min_price:
        products = products.filter(price__gte=Decimal(min_price))
    if max_price:
        products = products.filter(price__gte=Decimal(max_price))
    
    # Apply rating filter
    if rating:
        # This would require a review model to filter by average rating
        pass
    
    # Apply sorting
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'popularity':
        # Sort by sales count or views
        products = products.annotate(
            order_count=Count('orderitem')
        ).order_by('-order_count')
    elif sort_by == 'rating':
        # Sort by average rating (would require review model)
        pass
    
    # Get price range for filter UI
    price_range = Product.objects.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    # Get categories for filter UI
    categories = Product.objects.values('category').annotate(
        count=Count('id')
    ).order_by('category')
    
    # Get brands for filter UI
    brands = Product.objects.values('brand').annotate(
        count=Count('id')
    ).order_by('brand')
    
    # Implement pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'query': query,
        'category': category,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'brand': brand,
        'rating': rating,
        'price_range': price_range,
        'categories': categories,
        'brands': brands,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    
    return render(request, 'store/advanced_search.html', context)

def payment_view(request, order_id):
    """Payment view"""
    return render(request, 'store/payment.html')

@login_required
def share_wishlist(request):
    """Share wishlist"""
    from django.apps import apps
    from django.contrib import messages
    from django.http import JsonResponse
    import json
    
    Wishlist = apps.get_model('store', 'Wishlist')
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Get user's wishlist items
            wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
            
            # Create shareable data
            wishlist_data = []
            for item in wishlist_items:
                wishlist_data.append({
                    'name': item.product.name,
                    'price': str(item.product.price),
                    'currency': item.product.currency,
                    'product_id': item.product.id
                })
            
            # In a real implementation, you would generate a shareable link
            # For now, we'll just return success
            return JsonResponse({
                'success': True,
                'message': 'تم إنشاء رابط المشاركة بنجاح',
                'wishlist_count': len(wishlist_data)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'حدث خطأ أثناء مشاركة قائمة المفضلة'
            })
    
    messages.error(request, 'طلب غير صالح')
    return JsonResponse({'success': False, 'message': 'طلب غير صالح'})

@login_required
def clear_wishlist(request):
    """Clear all items from wishlist"""
    from django.apps import apps
    from django.contrib import messages
    
    Wishlist = apps.get_model('store', 'Wishlist')
    
    # Delete all wishlist items for the user
    Wishlist.objects.filter(user=request.user).delete()
    
    messages.success(request, 'تم مسح قائمة المفضلة بنجاح')
    return redirect('view_wishlist')

@login_required
def move_wishlist_to_cart(request):
    """Move all wishlist items to cart"""
    from django.apps import apps
    from django.contrib import messages
    
    Wishlist = apps.get_model('store', 'Wishlist')
    
    # Get all wishlist items
    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    if wishlist_items.exists():
        # Add each item to cart
        cart = Cart(request.session)
        added_count = 0
        
        for item in wishlist_items:
            cart.add(item.product.id, 1)
            added_count += 1
        
        messages.success(request, f'تم نقل {added_count} منتج إلى السلة')
        
        # Optionally clear wishlist after moving
        # wishlist_items.delete()
    else:
        messages.info(request, 'قائمة المفضلة فارغة')
    
    return redirect('view_wishlist')

@login_required
def create_stripe_payment_intent(request, order_id):
    """Create Stripe payment intent"""
    # Check if user is authorized to access this order
    from django.apps import apps
    Order = apps.get_model('store', 'Order')
    
    try:
        order = Order.objects.get(id=order_id)
        # Check if order belongs to the user or user is staff
        if order.user != request.user and not request.user.is_staff:
            return JsonResponse({'status': 'error', 'message': 'ليس لديك صلاحية الوصول إلى هذا الطلب'}, status=403)
    except Order.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'الطلب غير موجود'}, status=404)
    
    # Log the payment intent creation for security monitoring
    from .models import SecurityLog
    SecurityLog.objects.create(
        user=request.user,
        event_type='payment_intent_created',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        details=f'Payment intent created for order {order_id}'
    )
    
    return JsonResponse({'status': 'success'})

@login_required
def create_paypal_payment(request, order_id):
    """Create PayPal payment"""
    # Check if user is authorized to access this order
    from django.apps import apps
    Order = apps.get_model('store', 'Order')
    
    try:
        order = Order.objects.get(id=order_id)
        # Check if order belongs to the user or user is staff
        if order.user != request.user and not request.user.is_staff:
            return JsonResponse({'status': 'error', 'message': 'ليس لديك صلاحية الوصول إلى هذا الطلب'}, status=403)
    except Order.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'الطلب غير موجود'}, status=404)
    
    # Log the PayPal payment creation for security monitoring
    from .models import SecurityLog
    SecurityLog.objects.create(
        user=request.user,
        event_type='paypal_payment_created',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        details=f'PayPal payment created for order {order_id}'
    )
    
    return JsonResponse({'status': 'success'})

@login_required
def execute_paypal_payment(request, payment_id):
    """Execute PayPal payment"""
    # Log the PayPal payment execution for security monitoring
    from .models import SecurityLog
    SecurityLog.objects.create(
        user=request.user,
        event_type='paypal_payment_executed',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        details=f'PayPal payment executed with payment ID {payment_id}'
    )
    
    return JsonResponse({'status': 'success'})

def stripe_webhook(request):
    """Stripe webhook"""
    # Log webhook access for security monitoring
    from .models import SecurityLog
    SecurityLog.objects.create(
        event_type='stripe_webhook_accessed',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        details='Stripe webhook endpoint accessed'
    )
    
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
            # Cart is a utility class, not a model
            
            # Get coupon
            try:
                coupon = Coupon.objects.get(
                    code=coupon_code,
                    active=True,
                    valid_from__lte=timezone.now(),
                    valid_to__gte=timezone.now()
                )
            except Coupon.DoesNotExist:
                # Log failed coupon attempts for security monitoring
                from .models import SecurityLog
                SecurityLog.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    event_type='coupon_failed',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    details=f'Failed coupon attempt with code: {coupon_code}',
                    is_suspicious=True
                )
                return JsonResponse({'status': 'error', 'message': 'الكوبون غير صالح أو منتهي الصلاحية'})
            
            # Check usage limit
            if coupon.usage_limit and coupon.times_used >= coupon.usage_limit:
                # Log suspicious coupon usage attempts
                from .models import SecurityLog
                SecurityLog.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    event_type='coupon_limit_exceeded',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    details=f'Coupon limit exceeded for code: {coupon_code}',
                    is_suspicious=True
                )
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

@login_required
def coupon_management(request):
    """Coupon management view"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى إدارة الكوبونات')
        return redirect('home')
    
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

@login_required
def delete_coupon(request, coupon_id):
    """Delete coupon"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية حذف الكوبونات')
        return redirect('home')
    
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

@login_required
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

@login_required
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

@login_required
def loyalty_program_management(request):
    """Loyalty program management view"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى إدارة برنامج الولاء')
        return redirect('home')
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

@login_required
def delete_loyalty_reward(request, reward_id):
    """Delete loyalty reward"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية حذف مكافآت الولاء')
        return redirect('home')
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

@login_required
def email_campaigns(request):
    """Email campaigns view with full CRUD functionality"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى الحملات البريدية')
        return redirect('home')
    
    # Import model
    from django.apps import apps
    EmailCampaign = apps.get_model('store', 'EmailCampaign')
    
    if request.method == 'POST':
        # Get form data
        campaign_id = request.POST.get('campaign_id', '')
        subject = request.POST.get('subject', '')
        content = request.POST.get('content', '')
        recipients = request.POST.get('recipients', '')
        
        if subject and content and recipients:
            # Validate email addresses
            email_list = [email.strip() for email in recipients.split(',') if email.strip()]
            valid_emails = []
            for email in email_list:
                if '@' in email and '.' in email:
                    valid_emails.append(email)
            
            if valid_emails:
                if campaign_id:
                    # Edit existing campaign (only if it's still a draft)
                    try:
                        campaign = EmailCampaign.objects.get(id=campaign_id)
                        if campaign.status != 'draft':
                            messages.error(request, 'لا يمكن تعديل الحملة بعد إرسالها أو جدولتها!')
                            return redirect('email_campaigns')
                        
                        campaign.subject = subject
                        campaign.content = content
                        campaign.recipients = ','.join(valid_emails)
                        campaign.save()
                        messages.success(request, 'تم تحديث الحملة البريدية بنجاح!')
                    except EmailCampaign.DoesNotExist:
                        messages.error(request, 'الحملة غير موجودة!')
                else:
                    # Create new campaign
                    campaign = EmailCampaign.objects.create(
                        subject=subject,
                        content=content,
                        recipients=','.join(valid_emails),
                        status='draft'
                    )
                    messages.success(request, 'تم إنشاء الحملة البريدية بنجاح!')
                return redirect('email_campaigns')
            else:
                messages.error(request, 'يرجى إدخال عناوين بريد إلكتروني صحيحة.')
        else:
            messages.error(request, 'يرجى ملء جميع الحقول المطلوبة.')
    
    # Get all campaigns
    campaigns = EmailCampaign.objects.all().order_by('-created_at')
    
    context = {
        'campaigns': campaigns
    }
    
    return render(request, 'store/email_campaigns.html', context)

@login_required
def send_email_campaign(request, campaign_id):
    """Send email campaign"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية إرسال الحملات البريدية')
        return redirect('home')
    
    # Import model
    from django.apps import apps
    EmailCampaign = apps.get_model('store', 'EmailCampaign')
    
    try:
        campaign = EmailCampaign.objects.get(id=campaign_id)
        
        if campaign.status == 'sent':
            messages.error(request, 'هذه الحملة تم إرسالها بالفعل!')
            return redirect('email_campaigns')
        
        if campaign.status == 'cancelled':
            messages.error(request, 'لا يمكن إرسال حملة ملغاة!')
            return redirect('email_campaigns')
        
        # Send emails (simulated)
        # In a real implementation, you would use Django's email functionality
        # For example:
        # from django.core.mail import send_mail
        # recipient_list = [email.strip() for email in campaign.recipients.split(',')]
        # send_mail(
        #     campaign.subject,
        #     campaign.content,
        #     'from@example.com',  # sender
        #     recipient_list,
        #     fail_silently=False,
        # )
        
        # Update campaign status
        from django.utils import timezone
        campaign.status = 'sent'
        campaign.sent_at = timezone.now()
        campaign.save()
        
        messages.success(request, f'تم إرسال الحملة "{campaign.subject}" بنجاح!')
    except EmailCampaign.DoesNotExist:
        messages.error(request, 'الحملة غير موجودة!')
    
    return redirect('email_campaigns')

@login_required
def delete_email_campaign(request, campaign_id):
    """Delete email campaign"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية حذف الحملات البريدية')
        return redirect('home')
    
    # Import model
    from django.apps import apps
    EmailCampaign = apps.get_model('store', 'EmailCampaign')
    
    try:
        campaign = EmailCampaign.objects.get(id=campaign_id)
        
        # Delete campaign
        campaign_name = campaign.subject
        campaign.delete()
        
        messages.success(request, f'تم حذف الحملة "{campaign_name}" بنجاح!')
    except EmailCampaign.DoesNotExist:
        messages.error(request, 'الحملة غير موجودة!')
    
    return redirect('email_campaigns')

def get_recommendations(request):
    """Get recommendations"""
    return render(request, 'store/recommendations.html')

def track_user_behavior(request):
    """Track user behavior"""
    return JsonResponse({'status': 'success'})


def health_check(request):
    """Health check endpoint for load balancer and monitoring"""
    try:
        # Check database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "OK"
            
        # Check Redis connection
        import redis
        redis_client = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/1'))
        redis_client.ping()
        redis_status = "OK"
        
        # Check if DEBUG is disabled in production
        from django.conf import settings
        debug_status = "OK" if not settings.DEBUG else "WARNING - DEBUG is enabled"
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": {
                    "status": db_status
                },
                "redis": {
                    "status": redis_status
                },
                "debug": {
                    "status": debug_status
                }
            }
        }
        
        status_code = 200 if db_status == "OK" and redis_status == "OK" else 503
        return JsonResponse(health_data, status=status_code)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JsonResponse({
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }, status=503)

@login_required
def advertising_campaigns(request):
    """Advertising campaigns view"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى الحملات الإعلانية')
        return redirect('home')
    return render(request, 'store/advertising_campaigns.html')

@login_required
def delete_advertising_campaign(request, campaign_id):
    """Delete advertising campaign"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية حذف الحملات الإعلانية')
        return redirect('home')
    return redirect('advertising_campaigns')

@login_required
def social_media_integration(request):
    """Social media integration view"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى تكامل وسائل التواصل الاجتماعي')
        return redirect('home')
    
    # Import models
    from django.apps import apps
    from store.services.social_media_service import social_media_service
    SocialMediaIntegration = apps.get_model('store', 'SocialMediaIntegration')
    Product = apps.get_model('store', 'Product')
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        platform = request.POST.get('platform')
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Get or create integration record
            integration, created = SocialMediaIntegration.objects.get_or_create(
                product=product,
                platform=platform,
                defaults={'status': 'pending'}
            )
            
            # If integration already existed, reset status to pending for re-processing
            if not created:
                integration.status = 'pending'
                integration.save()
            
            # Attempt to post to the platform
            result = social_media_service.post_product_to_platform(integration)
            
            if result['success']:
                integration.status = 'posted'
                integration.post_id = result.get('post_id') or result.get('media_id')
                messages.success(request, f'تم نشر المنتج على {integration.get_platform_display()} بنجاح')
            else:
                integration.status = 'failed'
                messages.error(request, f'فشل نشر المنتج على {integration.get_platform_display()}: {result.get("error", "خطأ غير معروف")}')
            
            integration.save()
            
        except Product.DoesNotExist:
            messages.error(request, 'المنتج المحدد غير موجود')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء إنشاء التكامل: {str(e)}')
    
    # Get all products for the dropdown
    products = Product.objects.all()
    
    # Get existing integrations
    integrations = SocialMediaIntegration.objects.select_related('product').all()
    
    context = {
        'products': products,
        'integrations': integrations
    }
    
    return render(request, 'store/social_media_integration.html', context)

@login_required
def delete_social_media_integration(request, integration_id):
    """Delete social media integration"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية حذف تكامل وسائل التواصل الاجتماعي')
        return redirect('home')
    return redirect('social_media_integration')

@login_required
def shipping_integration(request):
    """Shipping integration view"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى تكامل الشحن')
        return redirect('home')
    
    # Import models
    from django.apps import apps
    from store.services.shipping_service import shipping_service
    ShippingIntegration = apps.get_model('store', 'ShippingIntegration')
    Order = apps.get_model('store', 'Order')
    
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        provider = request.POST.get('provider')
        
        try:
            order = Order.objects.get(id=order_id)
            
            # Get or create integration record
            integration, created = ShippingIntegration.objects.get_or_create(
                order=order,
                provider=provider,
                defaults={'status': 'pending'}
            )
            
            # If integration already existed, reset status to pending for re-processing
            if not created:
                integration.status = 'pending'
                integration.save()
            
            # Attempt to create shipment with the provider
            result = shipping_service.create_shipment(integration)
            
            if result['success']:
                integration.status = 'shipped'
                integration.tracking_number = result.get('tracking_number')
                messages.success(request, f'تم إنشاء الشحنة مع {integration.get_provider_display()} بنجاح')
            else:
                integration.status = 'failed'
                messages.error(request, f'فشل إنشاء الشحنة مع {integration.get_provider_display()}: {result.get("error", "خطأ غير معروف")}')
            
            integration.save()
            
        except Order.DoesNotExist:
            messages.error(request, 'الطلب المحدد غير موجود')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء إنشاء التكامل: {str(e)}')
    
    # Get all orders for the dropdown
    orders = Order.objects.all()
    
    # Get existing integrations
    integrations = ShippingIntegration.objects.select_related('order').all()
    
    context = {
        'orders': orders,
        'integrations': integrations
    }
    
    return render(request, 'store/shipping_integration.html', context)

@login_required
def delete_shipping_integration(request, integration_id):
    """Delete shipping integration"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية حذف تكامل الشحن')
        return redirect('home')
    return redirect('shipping_integration')

@login_required
def external_inventory(request):
    """External inventory view"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى المخزون الخارجي')
        return redirect('home')
    
    # Import models
    from django.apps import apps
    from store.services.external_inventory_service import external_inventory_service
    ExternalInventory = apps.get_model('store', 'ExternalInventory')
    Product = apps.get_model('store', 'Product')
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        external_id = request.POST.get('external_id')
        system_name = request.POST.get('system_name')
        api_endpoint = request.POST.get('api_endpoint', '')
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Get or create external inventory record
            inventory, created = ExternalInventory.objects.get_or_create(
                product=product,
                external_id=external_id,
                system_name=system_name,
                api_endpoint=api_endpoint,
                defaults={'sync_status': 'pending'}
            )
            
            # If inventory already existed, reset status to pending for re-processing
            if not created:
                inventory.sync_status = 'pending'
                inventory.save()
            
            # Attempt to sync with the external system
            result = external_inventory_service.sync_inventory(inventory)
            
            if result['success']:
                inventory.sync_status = 'synced'
                inventory.external_stock = result.get('stock', 0)
                messages.success(request, f'تمت مزامنة المخزون مع {system_name} بنجاح')
            else:
                inventory.sync_status = 'failed'
                messages.error(request, f'فشل مزامنة المخزون مع {system_name}: {result.get("error", "خطأ غير معروف")}')
            
            inventory.save()
            
        except Product.DoesNotExist:
            messages.error(request, 'المنتج المحدد غير موجود')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء إنشاء المزامنة: {str(e)}')
    
    # Get all products for the dropdown
    products = Product.objects.all()
    
    # Get existing inventory syncs
    inventories = ExternalInventory.objects.select_related('product').all()
    
    context = {
        'products': products,
        'inventories': inventories
    }
    
    return render(request, 'store/external_inventory.html', context)

@login_required
def delete_external_inventory(request, inventory_id):
    """Delete external inventory"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية حذف المخزون الخارجي')
        return redirect('home')
    return redirect('external_inventory')

@login_required
def accounting_integration(request):
    """Accounting integration view"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى تكامل المحاسبة')
        return redirect('home')
    return render(request, 'store/accounting_integration.html')

@login_required
def delete_accounting_integration(request, integration_id):
    """Delete accounting integration"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية حذف تكامل المحاسبة')
        return redirect('home')
    return redirect('accounting_integration')

@login_required
def analytics_integration(request):
    """Analytics integration view with AI-powered business intelligence"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية الوصول إلى تكامل التحليلات')
        return redirect('home')
    
    # Import models and services
    from django.apps import apps
    from store.services.analytics_service import analytics_service
    
    # Get advanced analytics data
    basic_data = analytics_service.get_basic_analytics()
    sales_data = analytics_service.get_sales_analytics()
    user_data = analytics_service.get_user_analytics()
    ai_insights = analytics_service.get_ai_insights()
    real_time_data = analytics_service.get_real_time_dashboard_data()
    advanced_real_time_data = analytics_service.get_advanced_real_time_data()
    predictive_data = analytics_service.get_predictive_analytics()
    
    context = {
        'basic_data': basic_data.get('data', {}) if basic_data.get('success') else {},
        'sales_data': sales_data.get('data', {}) if sales_data.get('success') else {},
        'user_data': user_data.get('data', {}) if user_data.get('success') else {},
        'ai_insights': ai_insights.get('data', {}).get('insights', []) if ai_insights.get('success') else [],
        'real_time_data': real_time_data.get('data', {}) if real_time_data.get('success') else {},
        'advanced_real_time_data': advanced_real_time_data.get('data', {}) if advanced_real_time_data.get('success') else {},
        'predictive_data': predictive_data.get('data', {}) if predictive_data.get('success') else {},
    }
    
    return render(request, 'store/analytics_integration.html', context)

@login_required
def track_analytics_event(request):
    """Track analytics event"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'ليس لديك صلاحية تتبع الأحداث التحليلية'})
    return JsonResponse({'status': 'success'})

@login_required
def export_analytics_report(request, format):
    """Export analytics report in specified format"""
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية تصدير التقارير التحليلية')
        return redirect('home')
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
