# Minimal views.py file with essential functions

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