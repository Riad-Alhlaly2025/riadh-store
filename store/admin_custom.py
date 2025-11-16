from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import (
    Product, Order, OrderItem, Notification, Commission, CommissionSettings,
    Payment, UserProfile, Coupon, LoyaltyProgram, EmailCampaign,
    AdvertisementCampaign, ShippingCompany, TaxRate, Review, Dispute,
    ShippingIntegration, AccountingIntegration, AnalyticsIntegration,
    MFADevice, SecurityLog, SensitiveData, Page, Article, LandingPage,
    FAQCategory, FAQ, EnhancedReview
)
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth, TruncDay
from django.contrib.admin.views.main import ChangeList
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


class CustomAdminSite(AdminSite):
    site_header = 'متجر رياض الإلكتروني - لوحة الإدارة'
    site_title = 'متجر رياض'
    index_title = 'لوحة التحكم الرئيسية'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
            path('commission-report/', self.admin_view(self.commission_report_view), name='commission_report'),
            path('sales-report/', self.admin_view(self.sales_report_view), name='sales_report'),
            path('store-settings/', self.admin_view(self.store_settings_view), name='store_settings'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        """Custom dashboard view with enhanced metrics"""
        # Get key metrics
        total_products = Product.objects.count()
        total_orders = Order.objects.count()
        total_users = User.objects.count()
        total_revenue = Order.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Get recent orders
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
        
        # Get top products by sales
        top_products = Product.objects.annotate(
            total_sales=Sum('orderitem__quantity')
        ).order_by('-total_sales')[:5]
        
        # Get sales by category
        sales_by_category = Product.objects.values('category').annotate(
            total_sales=Sum('orderitem__quantity'),
            total_revenue=Sum('orderitem__quantity') * Avg('price')
        ).order_by('-total_revenue')
        
        context = dict(
            self.each_context(request),
            total_products=total_products,
            total_orders=total_orders,
            total_users=total_users,
            total_revenue=total_revenue,
            recent_orders=recent_orders,
            top_products=top_products,
            sales_by_category=sales_by_category,
        )
        return render(request, 'admin/custom_dashboard.html', context)

    def commission_report_view(self, request):
        """Enhanced commission report view"""
        # Get commission statistics
        total_commissions = Commission.objects.count()
        total_commission_amount = Commission.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        paid_commissions = Commission.objects.filter(is_paid=True).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        pending_commissions = Commission.objects.filter(is_paid=False).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Get commissions by user role
        commissions_by_role = Commission.objects.values(
            'user__userprofile__role'
        ).annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('-total_amount')
        
        # Get recent commissions
        recent_commissions = Commission.objects.select_related(
            'user', 'order'
        ).order_by('-created_at')[:20]
        
        # Get commission trends (monthly)
        commission_trends = Commission.objects.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('month')
        
        context = dict(
            self.each_context(request),
            total_commissions=total_commissions,
            total_commission_amount=total_commission_amount,
            paid_commissions=paid_commissions,
            pending_commissions=pending_commissions,
            commissions_by_role=commissions_by_role,
            recent_commissions=recent_commissions,
            commission_trends=json.dumps(list(commission_trends), default=str),
        )
        return render(request, 'admin/commission_report.html', context)

    def sales_report_view(self, request):
        """Enhanced sales report view"""
        # Get sales statistics
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Get sales by status
        sales_by_status = Order.objects.values('status').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        ).order_by('-total')
        
        # Get sales by payment method
        sales_by_payment = Payment.objects.values('payment_method').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('-total')
        
        # Get top selling products
        top_products = Product.objects.annotate(
            total_sold=Sum('orderitem__quantity'),
            total_revenue=Sum('orderitem__quantity') * Avg('price')
        ).filter(total_sold__gt=0).order_by('-total_revenue')[:10]
        
        # Get sales trends (daily for last 30 days)
        sales_trends = Order.objects.annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        ).order_by('day')[:30]
        
        context = dict(
            self.each_context(request),
            total_orders=total_orders,
            total_revenue=total_revenue,
            sales_by_status=sales_by_status,
            sales_by_payment=sales_by_payment,
            top_products=top_products,
            sales_trends=json.dumps(list(sales_trends), default=str),
        )
        return render(request, 'admin/sales_report.html', context)

    def store_settings_view(self, request):
        """Enhanced store settings view"""
        # Get settings statistics
        total_users = User.objects.count()
        total_products = Product.objects.count()
        total_orders = Order.objects.count()
        
        # Get user roles distribution
        user_roles = UserProfile.objects.values('role').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Get product categories distribution
        product_categories = Product.objects.values('category').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Get recent activities
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
        recent_users = User.objects.order_by('-date_joined')[:5]
        
        context = dict(
            self.each_context(request),
            total_users=total_users,
            total_products=total_products,
            total_orders=total_orders,
            user_roles=user_roles,
            product_categories=product_categories,
            recent_orders=recent_orders,
            recent_users=recent_users,
        )
        return render(request, 'admin/store_settings.html', context)


# Create custom admin site instance
custom_admin_site = CustomAdminSite(name='custom_admin')


# Register models with enhanced admin classes
class EnhancedModelAdmin(admin.ModelAdmin):
    """Base enhanced admin class with common features"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Add any common queryset enhancements here
        return qs
    
    def get_list_display(self, request):
        # Add common list display enhancements
        return super().get_list_display(request)
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)


class ProductAdmin(EnhancedModelAdmin):
    list_display = ('name', 'price', 'category', 'stock_quantity', 'seller')
    list_filter = ('category', 'seller')
    search_fields = ('name', 'description')
    readonly_fields = ('in_stock', 'is_low_stock')
    list_per_page = 25


class OrderAdmin(EnhancedModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('user__username', 'id')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25


class CommissionAdmin(EnhancedModelAdmin):
    list_display = ('user', 'order', 'amount', 'rate', 'is_paid', 'created_at')
    list_filter = ('is_paid', 'created_at', 'user')
    search_fields = ('user__username', 'order__id')
    list_per_page = 25
    
    # Add custom actions
    actions = ['mark_as_paid', 'mark_as_unpaid']
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(is_paid=True)
        self.message_user(request, f'تم تحديث {updated} عمولة كمدفوعة.')
    mark_as_paid.short_description = "标记为已支付"
    
    def mark_as_unpaid(self, request, queryset):
        updated = queryset.update(is_paid=False)
        self.message_user(request, f'تم تحديث {updated} عمولة كغير مدفوعة.')
    mark_as_unpaid.short_description = "标记为未支付"


class UserAdmin(EnhancedModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_per_page = 25


# Register all models with the custom admin site
custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Product, ProductAdmin)
custom_admin_site.register(Order, OrderAdmin)
custom_admin_site.register(OrderItem, EnhancedModelAdmin)
custom_admin_site.register(Notification, EnhancedModelAdmin)
custom_admin_site.register(Commission, CommissionAdmin)
custom_admin_site.register(CommissionSettings, EnhancedModelAdmin)
custom_admin_site.register(Payment, EnhancedModelAdmin)
custom_admin_site.register(UserProfile, EnhancedModelAdmin)
custom_admin_site.register(Coupon, EnhancedModelAdmin)
custom_admin_site.register(LoyaltyProgram, EnhancedModelAdmin)
custom_admin_site.register(EmailCampaign, EnhancedModelAdmin)
custom_admin_site.register(AdvertisementCampaign, EnhancedModelAdmin)
custom_admin_site.register(ShippingCompany, EnhancedModelAdmin)
custom_admin_site.register(TaxRate, EnhancedModelAdmin)
custom_admin_site.register(Review, EnhancedModelAdmin)
custom_admin_site.register(Dispute, EnhancedModelAdmin)
custom_admin_site.register(ShippingIntegration, EnhancedModelAdmin)
custom_admin_site.register(AccountingIntegration, EnhancedModelAdmin)
custom_admin_site.register(AnalyticsIntegration, EnhancedModelAdmin)
custom_admin_site.register(MFADevice, EnhancedModelAdmin)
custom_admin_site.register(SecurityLog, EnhancedModelAdmin)
custom_admin_site.register(SensitiveData, EnhancedModelAdmin)
custom_admin_site.register(Page, EnhancedModelAdmin)
custom_admin_site.register(Article, EnhancedModelAdmin)
custom_admin_site.register(LandingPage, EnhancedModelAdmin)
custom_admin_site.register(FAQCategory, EnhancedModelAdmin)
custom_admin_site.register(FAQ, EnhancedModelAdmin)
custom_admin_site.register(EnhancedReview, EnhancedModelAdmin)