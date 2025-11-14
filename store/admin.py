from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Product, Order, OrderItem, Notification, Commission, CommissionSettings,
    Payment, Wishlist, Review, ProductComparison, Dispute, ShippingCompany,
    TaxRate, UserProfile, Coupon, LoyaltyProgram, LoyaltyReward, EmailCampaign,
    UserRecommendation, AdvertisementCampaign, UserBehavior, SocialMediaIntegration,
    ShippingIntegration, ExternalInventory, AccountingIntegration, AnalyticsIntegration,
    MFADevice, SecurityLog, SensitiveData
)
from .admin_mixins import VisualizationAdmin

# Register your models here.

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'ملفات المستخدمين'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_per_page = 25
    
    # Add date hierarchy
    date_hierarchy = 'date_joined'


class ProductAdmin(VisualizationAdmin):
    list_display = ('name', 'price', 'category', 'stock_quantity', 'seller')
    list_filter = ('category', 'seller')
    search_fields = ('name', 'description')
    readonly_fields = ('in_stock', 'is_low_stock')
    list_per_page = 25
    
    # Add actions
    actions = ['make_published', 'make_draft']
    
    @admin.action(description="نشر المنتجات المحددة")
    def make_published(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'تم نشر {updated} منتج.')
    
    @admin.action(description="تحويل المنتجات المحددة إلى مسودة")
    def make_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'تم تحويل {updated} منتج إلى مسودة.')


class OrderAdmin(VisualizationAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('user__username', 'id')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    
    # Add date hierarchy
    date_hierarchy = 'created_at'
    
    # Add actions
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
    @admin.action(description="标记为处理中")
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'تم تحديث {updated} طلب إلى قيد المعالجة.')
    
    @admin.action(description="标记为已发货")
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'تم تحديث {updated} طلب إلى تم الشحن.')
    
    @admin.action(description="标记为已交付")
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'تم تحديث {updated} طلب إلى تم التسليم.')
    
    @admin.action(description="标记为已取消")
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'تم تحديث {updated} طلب إلى ملغى.')


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order__status',)


class NotificationAdmin(VisualizationAdmin):
    list_display = ('user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')


class CommissionAdmin(VisualizationAdmin):
    list_display = ('user', 'order', 'amount', 'rate', 'is_paid', 'created_at')
    list_filter = ('is_paid', 'created_at', 'user')
    search_fields = ('user__username', 'order__id')
    list_per_page = 25
    
    # Add date hierarchy
    date_hierarchy = 'created_at'
    
    # Add actions
    actions = ['mark_as_paid', 'mark_as_unpaid']
    
    @admin.action(description="标记为已支付")
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(is_paid=True)
        self.message_user(request, f'تم تحديث {updated} عمولة كمدفوعة.')
    
    @admin.action(description="标记为未支付")
    def mark_as_unpaid(self, request, queryset):
        updated = queryset.update(is_paid=False)
        self.message_user(request, f'تم تحديث {updated} عمولة كغير مدفوعة.')


class CommissionSettingsAdmin(admin.ModelAdmin):
    list_display = ('user_role', 'product_category', 'commission_rate', 'is_active')
    list_filter = ('user_role', 'product_category', 'is_active')


class PaymentAdmin(VisualizationAdmin):
    list_display = ('order', 'payment_method', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('payment_method', 'currency', 'status', 'created_at')
    search_fields = ('order__id', 'transaction_id')


class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')


class ReviewAdmin(VisualizationAdmin):
    list_display = ('product', 'user', 'rating', 'is_verified_purchase', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'created_at')
    search_fields = ('user__username', 'product__name')


class ProductComparisonAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('created_at',)
    filter_horizontal = ('products',)


class DisputeAdmin(VisualizationAdmin):
    list_display = ('order', 'buyer', 'seller', 'status', 'resolution', 'created_at')
    list_filter = ('status', 'resolution', 'created_at')
    search_fields = ('order__id', 'buyer__username', 'seller__username')


class ShippingCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_cost', 'cost_per_kg', 'delivery_time', 'is_active')
    list_filter = ('is_active',)


class TaxRateAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')


# New admin registrations for missing features

class CouponAdmin(VisualizationAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'minimum_amount', 'active', 'valid_from', 'valid_to', 'times_used')
    list_filter = ('discount_type', 'active', 'valid_from', 'valid_to')
    search_fields = ('code',)
    readonly_fields = ('times_used',)


class LoyaltyProgramAdmin(VisualizationAdmin):
    list_display = ('user', 'points', 'level', 'total_spent', 'created_at')
    list_filter = ('level', 'created_at')
    search_fields = ('user__username',)


class LoyaltyRewardAdmin(admin.ModelAdmin):
    list_display = ('name', 'reward_type', 'points_required', 'discount_percentage', 'active')
    list_filter = ('reward_type', 'active')
    search_fields = ('name',)


class EmailCampaignAdmin(VisualizationAdmin):
    list_display = ('subject', 'status', 'scheduled_at', 'sent_at', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject',)


class UserRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')


class AdvertisementCampaignAdmin(VisualizationAdmin):
    list_display = ('name', 'platform', 'budget', 'spent', 'clicks', 'impressions', 'conversions', 'active')
    list_filter = ('platform', 'active', 'start_date', 'end_date')
    search_fields = ('name',)


class UserBehaviorAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'product', 'action', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__username', 'session_key')


# New admin registrations for integration features

class SocialMediaIntegrationAdmin(VisualizationAdmin):
    list_display = ('product', 'platform', 'status', 'created_at')
    list_filter = ('platform', 'status', 'created_at')
    search_fields = ('product__name',)


class ShippingIntegrationAdmin(VisualizationAdmin):
    list_display = ('order', 'provider', 'tracking_number', 'shipping_cost', 'status', 'created_at')
    list_filter = ('provider', 'status', 'created_at')
    search_fields = ('order__id', 'tracking_number')


class ExternalInventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'external_id', 'system_name', 'external_stock', 'sync_status', 'last_synced')
    list_filter = ('system_name', 'sync_status', 'last_synced')
    search_fields = ('product__name', 'external_id')


class AccountingIntegrationAdmin(VisualizationAdmin):
    list_display = ('order', 'accounting_system', 'transaction_id', 'sync_status', 'synced_at')
    list_filter = ('accounting_system', 'sync_status', 'synced_at')
    search_fields = ('order__id', 'transaction_id')


class AnalyticsIntegrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'event_type', 'product', 'order', 'timestamp')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('user__username', 'session_key')


# New admin registrations for security features

class MFADeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'device_type', 'is_active', 'created_at')
    list_filter = ('device_type', 'is_active', 'created_at')
    search_fields = ('user__username', 'name')


class SecurityLogAdmin(VisualizationAdmin):
    list_display = ('user', 'event_type', 'ip_address', 'is_suspicious', 'timestamp')
    list_filter = ('event_type', 'is_suspicious', 'timestamp')
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('timestamp',)


class SensitiveDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'data_type', 'encryption_method', 'created_at')
    list_filter = ('data_type', 'encryption_method', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register all models
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Commission, CommissionAdmin)
admin.site.register(CommissionSettings, CommissionSettingsAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(ProductComparison, ProductComparisonAdmin)
admin.site.register(Dispute, DisputeAdmin)
admin.site.register(ShippingCompany, ShippingCompanyAdmin)
admin.site.register(TaxRate, TaxRateAdmin)

# Register new models
admin.site.register(Coupon, CouponAdmin)
admin.site.register(LoyaltyProgram, LoyaltyProgramAdmin)
admin.site.register(LoyaltyReward, LoyaltyRewardAdmin)
admin.site.register(EmailCampaign, EmailCampaignAdmin)
admin.site.register(UserRecommendation, UserRecommendationAdmin)
admin.site.register(AdvertisementCampaign, AdvertisementCampaignAdmin)
admin.site.register(UserBehavior, UserBehaviorAdmin)

# Register new integration models
admin.site.register(SocialMediaIntegration, SocialMediaIntegrationAdmin)
admin.site.register(ShippingIntegration, ShippingIntegrationAdmin)
admin.site.register(ExternalInventory, ExternalInventoryAdmin)
admin.site.register(AccountingIntegration, AccountingIntegrationAdmin)
admin.site.register(AnalyticsIntegration, AnalyticsIntegrationAdmin)

# Register new security models
admin.site.register(MFADevice, MFADeviceAdmin)
admin.site.register(SecurityLog, SecurityLogAdmin)
admin.site.register(SensitiveData, SensitiveDataAdmin)