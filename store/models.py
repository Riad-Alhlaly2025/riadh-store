from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from typing import Any
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import BooleanField
from django.utils.text import slugify
import uuid


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('phones', 'هواتف'),
        ('computers', 'أجهزة كمبيوتر'),
        ('accessories', 'إكسسوارات'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('SAR', 'Saudi Riyal'),
        ('AED', 'UAE Dirham'),
        ('EGP', 'Egyptian Pound'),
        ('KWD', 'Kuwaiti Dinar'),
        ('QAR', 'Qatari Riyal'),
        ('OMR', 'Omani Rial'),
        ('BHD', 'Bahraini Dinar'),
        ('JOD', 'Jordanian Dinar'),
    ]

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, default="لا يوجد وصف")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='phones')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD', verbose_name='العملة')
    
    # Add seller field for multi-vendor support
    seller = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='البائع', null=True, blank=True)
    
    # Add inventory management fields
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name='كمية المخزون')
    low_stock_threshold = models.PositiveIntegerField(default=5, verbose_name='حد التنبيه عند انخفاض المخزون')
    
    # SEO fields
    seo_title = models.CharField(max_length=60, blank=True, verbose_name="عنوان SEO")
    seo_description = models.CharField(max_length=160, blank=True, verbose_name="وصف SEO")
    seo_keywords = models.CharField(max_length=255, blank=True, verbose_name="كلمات مفتاحية SEO")

    def __str__(self) -> str:
        return str(self.name)
    
    # Check if product is in stock
    @property
    def in_stock(self) -> bool:
        return self.stock_quantity > 0
    
    # Check if product is low in stock
    @property
    def is_low_stock(self) -> bool:
        return self.stock_quantity <= self.low_stock_threshold and self.stock_quantity > 0


class UserProfile(models.Model):
    USER_ROLES = [
        ('manager', 'مدير'),
        ('seller', 'بائع'),
        ('buyer', 'مشتري'),
    ]
    
    VERIFICATION_STATUS = [
        ('pending', 'قيد الانتظار'),
        ('approved', 'موافق عليه'),
        ('rejected', 'مرفوض'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='buyer', verbose_name='الدور')
    
    # Seller verification fields
    verification_status = models.CharField(max_length=10, choices=VERIFICATION_STATUS, default='pending', verbose_name='حالة التحقق')
    business_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='اسم النشاط التجاري')
    business_license = models.FileField(upload_to='licenses/', blank=True, null=True, verbose_name='الرخصة التجارية')
    id_document = models.FileField(upload_to='ids/', blank=True, null=True, verbose_name='صورة الهوية')
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name='رقم الهاتف')
    address = models.TextField(blank=True, null=True, verbose_name='العنوان')
    
    def __str__(self) -> str:
        # Handle the case where user might be None
        if self.user:
            return f"{self.user.username} - {self.get_role_display()}"  # type: ignore
        return f"UserProfile {self.pk}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance: User, created: bool, **kwargs) -> None:
    if created:
        UserProfile.objects.create(user=instance)  # type: ignore


@receiver(post_save, sender=User)
def save_user_profile(sender, instance: User, **kwargs) -> None:
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()  # type: ignore


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('processing', 'قيد المعالجة'),
        ('shipped', 'تم الشحن'),
        ('delivered', 'تم التسليم'),
        ('cancelled', 'ملغى'),
        ('dispute', 'نزاع'),  # Added for dispute resolution
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='المبلغ الإجمالي')
    shipping_address = models.TextField(verbose_name='عنوان التوصيل')
    phone_number = models.CharField(max_length=15, verbose_name='رقم الهاتف')
    
    # Shipping integration fields
    shipping_company = models.CharField(max_length=50, blank=True, null=True, verbose_name='شركة الشحن')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='تكلفة الشحن')
    tracking_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='رقم التتبع')
    
    # Tax calculation field
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='قيمة الضريبة')
    
    class Meta:
        verbose_name = 'طلب'
        verbose_name_plural = 'الطلبات'
        ordering = ['-created_at']

    def __str__(self) -> str:
        # Handle case where user might be None
        username = getattr(self.user, 'username', 'Unknown')
        return f"طلب #{self.pk} - {username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='الطلب')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='المنتج')
    quantity = models.PositiveIntegerField(verbose_name='الكمية')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='السعر')

    class Meta:
        verbose_name = 'عنصر الطلب'
        verbose_name_plural = 'عناصر الطلبات'

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self) -> Decimal:
        return Decimal(str(self.quantity)) * Decimal(str(self.price))


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('order_created', 'تم إنشاء الطلب'),
        ('order_status_changed', 'تغير حالة الطلب'),
        ('order_shipped', 'تم شحن الطلب'),
        ('order_delivered', 'تم تسليم الطلب'),
        ('commission_calculated', 'تم حساب العمولة'),  # New notification type for commissions
        ('low_stock', 'انخفاض المخزون'),  # For inventory management
        ('dispute_opened', 'فتح نزاع'),  # For dispute resolution
        ('dispute_resolved', 'حل النزاع'),  # For dispute resolution
        ('verification_status_changed', 'تغير حالة التحقق'),  # For seller verification
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='الطلب', null=True, blank=True)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, verbose_name='نوع الإشعار')
    message = models.TextField(verbose_name='الرسالة')
    is_read = models.BooleanField(default=False, verbose_name='مقروء')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        # Handle case where user might be None
        username = getattr(self.user, 'username', 'Unknown')
        notification_type_display = getattr(self, 'get_notification_type_display', lambda: 'Unknown')()
        return f"إشعار {notification_type_display} لـ {username}"


class Commission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='الطلب')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ العمولة')
    rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='نسبة العمولة (%)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    is_paid = models.BooleanField(default=False, verbose_name='تم الدفع')
    
    class Meta:
        verbose_name = 'عمولة'
        verbose_name_plural = 'العمولات'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        # Handle case where user or order might be None
        username = getattr(self.user, 'username', 'Unknown')
        order_pk = getattr(self.order, 'pk', 'Unknown')
        return f"عمولة {username} - طلب #{order_pk}"


class CommissionSettings(models.Model):
    USER_ROLE_CHOICES = [
        ('manager', 'مدير'),
        ('seller', 'بائع'),
        ('buyer', 'مشتري'),
    ]
    
    CATEGORY_CHOICES = [
        ('phones', 'هواتف'),
        ('computers', 'أجهزة كمبيوتر'),
        ('accessories', 'إكسسوارات'),
    ]
    
    user_role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES, verbose_name='دور المستخدم')
    product_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='فئة المنتج', blank=True, null=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='نسبة العمولة (%)', default=0.00)
    is_active = models.BooleanField(default=True, verbose_name='مفعل')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'إعدادات العمولة'
        verbose_name_plural = 'إعدادات العمولات'
        unique_together = ('user_role', 'product_category')
    
    def __str__(self) -> str:
        category = self.product_category if self.product_category else 'الكل'
        return f"عمولة {self.user_role} - {category}: {self.commission_rate}%"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('completed', 'مكتمل'),
        ('failed', 'فشل'),
        ('refunded', 'تم الاسترجاع'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('SAR', 'Saudi Riyal'),
        ('AED', 'UAE Dirham'),
        ('EGP', 'Egyptian Pound'),
        ('KWD', 'Kuwaiti Dinar'),
        ('QAR', 'Qatari Riyal'),
        ('OMR', 'Omani Rial'),
        ('BHD', 'Bahraini Dinar'),
        ('JOD', 'Jordanian Dinar'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name='الطلب')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name='طريقة الدفع')
    transaction_id = models.CharField(max_length=100, unique=True, verbose_name='معرف المعاملة')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='المبلغ')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD', verbose_name='العملة')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name='الحالة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'دفعة'
        verbose_name_plural = 'الدفعات'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        order_pk = getattr(self.order, 'pk', 'Unknown')
        status_display = getattr(self, 'get_status_display', lambda: 'Unknown')()
        return f"دفعة #{self.pk} - طلب #{order_pk} - {status_display}"


# New models for advanced features

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='المنتج')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'قائمة الرغبات'
        verbose_name_plural = 'قوائم الرغبات'
        unique_together = ('user', 'product')  # Prevent duplicate entries
    
    def __str__(self):
        username = getattr(self.user, 'username', 'Unknown User')
        return f"{username} - {self.product.name}"


class Review(models.Model):
    RATINGS = [
        (1, '1 - سيء'),
        (2, '2 - مقبول'),
        (3, '3 - جيد'),
        (4, '4 - جيد جداً'),
        (5, '5 - ممتاز'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='المنتج', related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    rating = models.IntegerField(choices=RATINGS, verbose_name='التقييم')
    comment = models.TextField(verbose_name='التعليق')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    is_verified_purchase = models.BooleanField(default=False, verbose_name='شراء مؤكد')  # To verify if user actually bought the product  # type: ignore[assignment]
    
    class Meta:
        verbose_name = 'مراجعة'
        verbose_name_plural = 'مراجعات'
        unique_together = ('user', 'product')  # One review per user per product
        ordering = ['-created_at']
    
    def __str__(self):
        username = getattr(self.user, 'username', 'Unknown User')
        return f"{username} - {self.product.name} - {self.rating}/5"


class ProductComparison(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم', null=True, blank=True)  # Allow anonymous comparisons
    products = models.ManyToManyField(Product, verbose_name='المنتجات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'مقارنة منتجات'
        verbose_name_plural = 'ممارسات مقارنة المنتجات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"مقارنة منتجات - {self.created_at}"


class Dispute(models.Model):
    DISPUTE_STATUS = [
        ('open', 'مفتوح'),
        ('in_progress', 'قيد المعالجة'),
        ('resolved', 'تم الحل'),
        ('closed', 'مغلق'),
    ]
    
    DISPUTE_RESOLUTION = [
        ('pending', 'قيد الانتظار'),
        ('buyer_favor', 'صالح المشتري'),
        ('seller_favor', 'صالح البائع'),
        ('refund', 'استرداد'),
        ('partial_refund', 'استرداد جزئي'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='الطلب')
    buyer = models.ForeignKey(User, related_name='disputes_as_buyer', on_delete=models.CASCADE, verbose_name='المشتري')
    seller = models.ForeignKey(User, related_name='disputes_as_seller', on_delete=models.CASCADE, verbose_name='البائع')
    reason = models.TextField(verbose_name='سبب النزاع')
    status = models.CharField(max_length=15, choices=DISPUTE_STATUS, default='open', verbose_name='الحالة')
    resolution = models.CharField(max_length=15, choices=DISPUTE_RESOLUTION, default='pending', verbose_name='الحل المقترح')
    resolution_notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات الحل')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'نزاع'
        verbose_name_plural = 'النزاعات'
        ordering = ['-created_at']
    
    def __str__(self):
        order_id = getattr(self.order, 'id', 'Unknown')
        status_display = getattr(self, 'get_status_display', lambda: 'Unknown')()
        return f"نزاع الطلب #{order_id} - {status_display}"


class ShippingCompany(models.Model):
    name = models.CharField(max_length=50, verbose_name='اسم الشركة')
    base_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='التكلفة الأساسية')
    cost_per_kg = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='التكلفة لكل كيلوغرام')
    delivery_time = models.CharField(max_length=50, verbose_name='وقت التسليم المتوقع')
    is_active = models.BooleanField(default=True, verbose_name='مفعل')  # type: ignore
    
    class Meta:
        verbose_name = 'شركة شحن'
        verbose_name_plural = 'شركات الشحن'
    
    def __str__(self):
        return str(self.name)


class TaxRate(models.Model):
    name = models.CharField(max_length=50, verbose_name='اسم الضريبة')
    rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='نسبة الضريبة (%)')
    is_active = models.BooleanField(default=True, verbose_name='مفعل')  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'معدل ضريبي'
        verbose_name_plural = 'معدلات ضريبية'
    
    def __str__(self):
        return f"{self.name} - {self.rate}%"


# New models for missing features

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'نسبة مئوية'),
        ('fixed', 'قيمة ثابتة'),
    ]
    
    code = models.CharField(max_length=20, unique=True, verbose_name='رمز الكوبون')
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, verbose_name='نوع الخصم')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قيمة الخصم')
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='الحد الأدنى للطلب')
    active = models.BooleanField(default=True, verbose_name='مفعل')  # type: ignore
    valid_from = models.DateTimeField(verbose_name='صالح من')
    valid_to = models.DateTimeField(verbose_name='صالح حتى')
    usage_limit = models.PositiveIntegerField(null=True, blank=True, verbose_name='حد الاستخدام')
    times_used = models.PositiveIntegerField(default=0, verbose_name='مرات الاستخدام')  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'كوبون'
        verbose_name_plural = 'كوبونات'
    
    def __str__(self) -> str:
        # Find the display value for the discount type
        discount_type_display = self.discount_type
        for choice in self.DISCOUNT_TYPE_CHOICES:
            if choice[0] == self.discount_type:
                discount_type_display = choice[1]
                break
        return f"{self.code} - {discount_type_display}"


class LoyaltyProgram(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    points = models.PositiveIntegerField(default=0, verbose_name='النقاط')  # type: ignore
    level = models.CharField(max_length=20, default='bronze', verbose_name='المستوى')
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='إجمالي الإنفاق')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'برنامج الولاء'
        verbose_name_plural = 'برامج الولاء'
    
    def __str__(self) -> str:
        try:
            user = self.user
            if user is not None:
                username = getattr(user, 'username', 'Unknown User')
            else:
                username = 'Unknown User'
        except:
            username = 'Unknown User'
        return f"{username} - {self.points} نقطة"


class LoyaltyReward(models.Model):
    REWARD_TYPE_CHOICES = [
        ('discount', 'خصم'),
        ('free_product', 'منتج مجاني'),
        ('shipping', 'شحن مجاني'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='اسم المكافأة')
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPE_CHOICES, verbose_name='نوع المكافأة')
    points_required = models.PositiveIntegerField(verbose_name='النقاط المطلوبة')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='نسبة الخصم')
    active = models.BooleanField(default=True, verbose_name='مفعل')  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'مكافأة الولاء'
        verbose_name_plural = 'مكافآت الولاء'
    
    def __str__(self) -> str:
        return str(self.name)


class EmailCampaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('scheduled', 'مجدول'),
        ('sent', 'مرسل'),
        ('cancelled', 'ملغى'),
    ]
    
    subject = models.CharField(max_length=200, verbose_name='الموضوع')
    content = models.TextField(verbose_name='المحتوى')
    recipients = models.TextField(help_text='قائمة البريد الإلكتروني مفصولة بفواصل', verbose_name='المستلمون')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='الحالة')
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name='مجدول في')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='أرسل في')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'حملة بريد إلكتروني'
        verbose_name_plural = 'حملات البريد الإلكتروني'
    
    def __str__(self) -> str:
        return str(self.subject)


class UserRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='المنتج')
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='النتيجة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'توصية المستخدم'
        verbose_name_plural = 'توصيات المستخدمين'
        unique_together = ('user', 'product')
    
    def __str__(self) -> str:
        try:
            user = self.user
            if user is not None:
                username = getattr(user, 'username', 'Unknown User')
            else:
                username = 'Unknown User'
        except:
            username = 'Unknown User'
            
        try:
            product = self.product
            if product is not None:
                product_name = getattr(product, 'name', 'Unknown Product')
            else:
                product_name = 'Unknown Product'
        except:
            product_name = 'Unknown Product'
        return f"{username} - {product_name}"


class AdvertisementCampaign(models.Model):
    PLATFORM_CHOICES = [
        ('facebook', 'فيسبوك'),
        ('google', 'جوجل'),
        ('instagram', 'إنستغرام'),
        ('twitter', 'تويتر'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='اسم الحملة')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, verbose_name='المنصة')
    budget = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='الميزانية')
    spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='المنفق')
    clicks = models.PositiveIntegerField(default=0, verbose_name='النقرات')  # type: ignore
    impressions = models.PositiveIntegerField(default=0, verbose_name='الظهور')  # type: ignore
    conversions = models.PositiveIntegerField(default=0, verbose_name='التحويلات')  # type: ignore
    start_date = models.DateTimeField(verbose_name='تاريخ البدء')
    end_date = models.DateTimeField(verbose_name='تاريخ الانتهاء')
    active = models.BooleanField(default=True, verbose_name='مفعل')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'حملة إعلانية'
        verbose_name_plural = 'حملات إعلانية'
    
    def __str__(self) -> str:
        return str(self.name)


class UserBehavior(models.Model):
    ACTION_CHOICES = [
        ('view', 'عرض'),
        ('click', 'نقر'),
        ('add_to_cart', 'إضافة للسلة'),
        ('purchase', 'شراء'),
        ('search', 'بحث'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='المستخدم')
    session_key = models.CharField(max_length=40, null=True, blank=True, verbose_name='مفتاح الجلسة')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, verbose_name='المنتج')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='الإجراء')
    metadata = models.TextField(blank=True, null=True, verbose_name='بيانات إضافية')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'سلوك المستخدم'
        verbose_name_plural = 'سلوكيات المستخدمين'
    
    def __str__(self) -> str:
        try:
            user = self.user
            if user is not None:
                user_display = getattr(user, 'username', self.session_key if self.session_key else 'Unknown')
            else:
                user_display = self.session_key if self.session_key else 'Unknown'
        except:
            user_display = self.session_key if self.session_key else 'Unknown'
        
        try:
            product = self.product
            if product is not None:
                product_display = getattr(product, 'name', 'N/A')
            else:
                product_display = 'N/A'
        except:
            product_display = 'N/A'
            
        return f"{user_display} - {self.action} - {product_display}"

# New models for integration features

class SocialMediaIntegration(models.Model):
    PLATFORM_CHOICES = [
        ('facebook', 'فيسبوك'),
        ('twitter', 'تويتر'),
        ('instagram', 'إنستغرام'),
        ('linkedin', 'لينكدإن'),
        ('pinterest', 'بينتيريست'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='المنتج')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, verbose_name='المنصة')
    post_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='معرف المنشور')
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name='مجدول في')
    posted_at = models.DateTimeField(null=True, blank=True, verbose_name='نُشر في')
    status = models.CharField(max_length=20, default='pending', verbose_name='الحالة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'تكامل وسائل التواصل'
        verbose_name_plural = 'تكاملات وسائل التواصل'
    
    def __str__(self) -> str:
        try:
            product = self.product
            if product is not None:
                product_name = getattr(product, 'name', 'Unknown Product')
            else:
                product_name = 'Unknown Product'
        except:
            product_name = 'Unknown Product'
            
        # Find the display value for the platform
        platform_display = self.platform
        for choice in self.PLATFORM_CHOICES:
            if choice[0] == self.platform:
                platform_display = choice[1]
                break
        return f"{product_name} - {platform_display}"


class ShippingIntegration(models.Model):
    SHIPPING_PROVIDER_CHOICES = [
        ('fedex', 'FedEx'),
        ('dhl', 'DHL'),
        ('ups', 'UPS'),
        ('aramex', 'Aramex'),
        ('smsa', 'SMSA'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name='الطلب')
    provider = models.CharField(max_length=20, choices=SHIPPING_PROVIDER_CHOICES, verbose_name='مزود الشحن')
    tracking_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='رقم التتبع')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='تكلفة الشحن')
    estimated_delivery = models.DateTimeField(null=True, blank=True, verbose_name='التسليم المتوقع')
    status = models.CharField(max_length=30, default='pending', verbose_name='الحالة')
    api_response = models.TextField(blank=True, null=True, verbose_name='استجابة API')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'تكامل الشحن'
        verbose_name_plural = 'تكاملات الشحن'
    
    def __str__(self) -> str:
        try:
            order = self.order
            if order is not None:
                order_id = getattr(order, 'pk', 'Unknown')
            else:
                order_id = 'Unknown'
        except:
            order_id = 'Unknown'
            
        # Find the display value for the provider
        provider_display = self.provider
        for choice in self.SHIPPING_PROVIDER_CHOICES:
            if choice[0] == self.provider:
                provider_display = choice[1]
                break
        return f"شحن الطلب #{order_id} - {provider_display}"


class ExternalInventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name='المنتج')
    external_id = models.CharField(max_length=100, verbose_name='المعرف الخارجي')
    system_name = models.CharField(max_length=50, verbose_name='اسم النظام')
    last_synced = models.DateTimeField(null=True, blank=True, verbose_name='آخر مزامنة')
    external_stock = models.PositiveIntegerField(default=0, verbose_name='المخزون الخارجي')  # type: ignore
    sync_status = models.CharField(max_length=20, default='pending', verbose_name='حالة المزامنة')
    api_endpoint = models.URLField(blank=True, null=True, verbose_name='نقطة نهاية API')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'مخزون خارجي'
        verbose_name_plural = 'المخزونات الخارجية'
    
    def __str__(self) -> str:
        try:
            product = self.product
            if product is not None:
                product_name = getattr(product, 'name', 'Unknown Product')
            else:
                product_name = 'Unknown Product'
        except:
            product_name = 'Unknown Product'
        return f"{product_name} - {self.system_name}"


class AccountingIntegration(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('processing', 'قيد المعالجة'),
        ('shipped', 'تم الشحن'),
        ('delivered', 'تم التسليم'),
        ('cancelled', 'ملغى'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name='الطلب')
    accounting_system = models.CharField(max_length=50, verbose_name='نظام المحاسبة')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='معرف المعاملة')
    synced_at = models.DateTimeField(null=True, blank=True, verbose_name='تمت المزامنة في')
    sync_status = models.CharField(max_length=20, default='pending', verbose_name='حالة المزامنة')
    accounting_data = models.TextField(blank=True, null=True, verbose_name='بيانات المحاسبة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'تكامل المحاسبة'
        verbose_name_plural = 'تكاملات المحاسبة'
    
    def __str__(self) -> str:
        try:
            order = self.order
            if order is not None:
                order_id = getattr(order, 'pk', 'Unknown')
            else:
                order_id = 'Unknown'
        except:
            order_id = 'Unknown'
        return f"طلب #{order_id} - {self.accounting_system}"


class AnalyticsIntegration(models.Model):
    EVENT_TYPE_CHOICES = [
        ('page_view', 'عرض الصفحة'),
        ('product_view', 'عرض المنتج'),
        ('add_to_cart', 'إضافة للسلة'),
        ('checkout', 'الدفع'),
        ('purchase', 'شراء'),
        ('search', 'بحث'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='المستخدم')
    session_key = models.CharField(max_length=40, null=True, blank=True, verbose_name='مفتاح الجلسة')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, verbose_name='نوع الحدث')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, verbose_name='المنتج')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, verbose_name='الطلب')
    url = models.URLField(blank=True, null=True, verbose_name='الرابط')
    referrer = models.URLField(blank=True, null=True, verbose_name='المرجع')
    user_agent = models.TextField(blank=True, null=True, verbose_name='وكيل المستخدم')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='عنوان IP')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='الطابع الزمني')
    metadata = models.TextField(blank=True, null=True, verbose_name='بيانات إضافية')
    
    class Meta:
        verbose_name = 'تحليلات'
        verbose_name_plural = 'التحليلات'
    
    def __str__(self) -> str:
        try:
            user = self.user
            if user is not None:
                user_display = getattr(user, 'username', self.session_key if self.session_key else 'Unknown')
            else:
                user_display = self.session_key if self.session_key else 'Unknown'
        except:
            user_display = self.session_key if self.session_key else 'Unknown'
        
        # Find the display value for the event type
        event_type_display = self.event_type
        for choice in self.EVENT_TYPE_CHOICES:
            if choice[0] == self.event_type:
                event_type_display = choice[1]
                break
        return f"{user_display} - {event_type_display} - {self.timestamp}"

# New models for security features

class MFADevice(models.Model):
    """Model for storing MFA devices for users"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    name = models.CharField(max_length=100, verbose_name='اسم الجهاز')
    secret_key = models.CharField(max_length=100, verbose_name='المفتاح السري')
    device_type = models.CharField(max_length=20, choices=[
        ('totp', 'TOTP (Time-based)'),
        ('hotp', 'HOTP (Counter-based)'),
    ], verbose_name='نوع الجهاز')
    is_active = models.BooleanField(default=True, verbose_name='مفعل')  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    last_used = models.DateTimeField(null=True, blank=True, verbose_name='آخر استخدام')
    
    class Meta:
        verbose_name = 'جهاز MFA'
        verbose_name_plural = 'أجهزة MFA'
    
    def __str__(self) -> str:
        try:
            user = self.user
            if user is not None:
                username = getattr(user, 'username', 'Unknown User')
            else:
                username = 'Unknown User'
        except:
            username = 'Unknown User'
        return f"{username} - {self.name}"


class SecurityLog(models.Model):
    """Model for storing security-related events"""
    EVENT_TYPES = [
        ('login_success', 'تسجيل دخول ناجح'),
        ('login_failed', 'تسجيل دخول فاشل'),
        ('logout', 'تسجيل خروج'),
        ('password_change', 'تغيير كلمة المرور'),
        ('mfa_success', 'MFA ناجح'),
        ('mfa_failed', 'MFA فاشل'),
        ('suspicious_activity', 'نشاط مشبوه'),
        ('account_lockout', 'قفل الحساب'),
        ('permission_change', 'تغيير الصلاحيات'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='المستخدم')
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES, verbose_name='نوع الحدث')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='عنوان IP')
    user_agent = models.TextField(blank=True, null=True, verbose_name='وكيل المستخدم')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='الطابع الزمني')
    details = models.TextField(blank=True, null=True, verbose_name='تفاصيل')
    is_suspicious = models.BooleanField(default=False, verbose_name='مشبوه')  # type: ignore
    
    class Meta:
        verbose_name = 'سجل أمان'
        verbose_name_plural = 'سجلات الأمان'
        ordering = ['-timestamp']
    
    def __str__(self) -> str:
        try:
            user = self.user
            if user is not None:
                user_display = getattr(user, 'username', 'Unknown')
            else:
                user_display = 'Unknown'
        except:
            user_display = 'Unknown'
        
        # Find the display value for the event type
        event_type_display = self.event_type
        for choice in self.EVENT_TYPES:
            if choice[0] == self.event_type:
                event_type_display = choice[1]
                break
        return f"{user_display} - {event_type_display} - {self.timestamp}"


class SensitiveData(models.Model):
    """Model for storing encrypted sensitive data"""
    DATA_TYPES = [
        ('credit_card', 'بطاقة ائتمان'),
        ('bank_account', 'حساب بنكي'),
        ('personal_id', 'هوية شخصية'),
        ('passport', 'جواز سفر'),
        ('address', 'عنوان'),
        ('phone', 'رقم هاتف'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    data_type = models.CharField(max_length=20, choices=DATA_TYPES, verbose_name='نوع البيانات')
    encrypted_data = models.TextField(verbose_name='البيانات المشفرة')
    encryption_method = models.CharField(max_length=50, default='AES-256', verbose_name='طريقة التشفير')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'بيانات حساسة'
        verbose_name_plural = 'بيانات حساسة'
    
    def __str__(self) -> str:
        try:
            user = self.user
            if user is not None:
                username = getattr(user, 'username', 'Unknown User')
            else:
                username = 'Unknown User'
        except:
            username = 'Unknown User'
            
        # Find the display value for the data type
        data_type_display = self.data_type
        for choice in self.DATA_TYPES:
            if choice[0] == self.data_type:
                data_type_display = choice[1]
                break
        return f"{username} - {data_type_display}"


# CMS Models for Content Management System

class Page(models.Model):
    """Model for managing store pages like About, Contact, etc."""
    PAGE_STATUS = [
        ('draft', 'مسودة'),
        ('published', 'منشور'),
        ('archived', 'مؤرشف'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='العنوان')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='الرابط')
    content = models.TextField(verbose_name='المحتوى')
    excerpt = models.TextField(blank=True, null=True, verbose_name='ملخص')
    featured_image = models.ImageField(upload_to='pages/', blank=True, null=True, verbose_name='الصورة الرئيسية')
    status = models.CharField(max_length=10, choices=PAGE_STATUS, default='draft', verbose_name='الحالة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ النشر')
    
    # SEO fields
    seo_title = models.CharField(max_length=60, blank=True, verbose_name="عنوان SEO")
    seo_description = models.CharField(max_length=160, blank=True, verbose_name="وصف SEO")
    seo_keywords = models.CharField(max_length=255, blank=True, verbose_name="كلمات مفتاحية SEO")
    
    class Meta:
        verbose_name = 'صفحة'
        verbose_name_plural = 'الصفحات'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return str(self.title)


class Article(models.Model):
    """Model for blog articles and news posts"""
    ARTICLE_STATUS = [
        ('draft', 'مسودة'),
        ('published', 'منشور'),
        ('archived', 'مؤرشف'),
    ]
    
    ARTICLE_TYPE = [
        ('blog', 'مدونة'),
        ('news', 'أخبار'),
        ('tutorial', 'شرح'),
        ('announcement', 'إعلان'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='العنوان')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='الرابط')
    content = models.TextField(verbose_name='المحتوى')
    excerpt = models.TextField(blank=True, null=True, verbose_name='ملخص')
    featured_image = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name='الصورة الرئيسية')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='الكاتب')
    status = models.CharField(max_length=10, choices=ARTICLE_STATUS, default='draft', verbose_name='الحالة')
    article_type = models.CharField(max_length=15, choices=ARTICLE_TYPE, default='blog', verbose_name='نوع المقال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ النشر')
    views = models.PositiveIntegerField(default=0, verbose_name='المشاهدات')
    
    # SEO fields
    seo_title = models.CharField(max_length=60, blank=True, verbose_name="عنوان SEO")
    seo_description = models.CharField(max_length=160, blank=True, verbose_name="وصف SEO")
    seo_keywords = models.CharField(max_length=255, blank=True, verbose_name="كلمات مفتاحية SEO")
    
    class Meta:
        verbose_name = 'مقال'
        verbose_name_plural = 'المقالات'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return str(self.title)


class LandingPage(models.Model):
    """Model for marketing landing pages"""
    LANDING_PAGE_STATUS = [
        ('draft', 'مسودة'),
        ('active', 'مفعلة'),
        ('inactive', 'غير مفعلة'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='اسم الصفحة')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='الرابط')
    title = models.CharField(max_length=200, verbose_name='العنوان الرئيسي')
    subtitle = models.CharField(max_length=300, blank=True, null=True, verbose_name='العنوان الفرعي')
    content = models.TextField(blank=True, null=True, verbose_name='المحتوى')
    call_to_action = models.CharField(max_length=100, blank=True, null=True, verbose_name='زر الدعوة لل действие')
    call_to_action_url = models.URLField(blank=True, null=True, verbose_name='رابط زر الدعوة لل действие')
    background_image = models.ImageField(upload_to='landing_pages/', blank=True, null=True, verbose_name='صورة الخلفية')
    status = models.CharField(max_length=10, choices=LANDING_PAGE_STATUS, default='draft', verbose_name='الحالة')
    campaign_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='اسم الحملة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    starts_at = models.DateTimeField(null=True, blank=True, verbose_name='يبدأ في')
    ends_at = models.DateTimeField(null=True, blank=True, verbose_name='ينتهي في')
    
    class Meta:
        verbose_name = 'صفحة هبوط'
        verbose_name_plural = 'صفحات الهبوط'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return str(self.name)


class Comment(models.Model):
    """Model for user comments on articles and pages"""
    COMMENT_STATUS = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'موافق عليه'),
        ('rejected', 'مرفوض'),
        ('spam', 'بريد مزعج'),
    ]
    
    content = models.TextField(verbose_name='المحتوى')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='الكاتب')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True, verbose_name='المقال')
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True, blank=True, verbose_name='الصفحة')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='التعليق الأصل')
    status = models.CharField(max_length=10, choices=COMMENT_STATUS, default='pending', verbose_name='الحالة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'تعليق'
        verbose_name_plural = 'التعليقات'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        try:
            user = self.author
            if user is not None:
                username = getattr(user, 'username', 'Unknown User')
            else:
                username = 'Unknown User'
        except:
            username = 'Unknown User'
        
        if self.article:
            try:
                article_title = getattr(self.article, 'title', 'مقال غير معروف')
                return f"تعليق من {username} على {article_title}"
            except:
                return f"تعليق من {username} على مقال"
        elif self.page:
            try:
                page_title = getattr(self.page, 'title', 'صفحة غير معروفة')
                return f"تعليق من {username} على {page_title}"
            except:
                return f"تعليق من {username} على صفحة"
        else:
            return f"تعليق من {username}"

# New models for customer support features

class LiveChatSession(models.Model):
    """Model for live chat sessions between customers and support agents"""
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('pending', 'قيد الانتظار'),
        ('closed', 'مغلق'),
        ('transferred', 'محول'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions_as_customer', verbose_name='العميل')
    support_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_sessions_as_agent', verbose_name='وكيل الدعم')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الإغلاق')
    topic = models.CharField(max_length=200, verbose_name='الموضوع')
    
    class Meta:
        verbose_name = 'جلسة دردشة مباشرة'
        verbose_name_plural = 'جلسات الدردشة المباشرة'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        customer_name = getattr(self.customer, 'username', 'Unknown Customer')
        agent_name = getattr(self.support_agent, 'username', 'No Agent') if self.support_agent else 'No Agent'
        return f"دردشة: {customer_name} مع {agent_name} - {self.topic}"

class LiveChatMessage(models.Model):
    """Model for individual messages in live chat sessions"""
    chat_session = models.ForeignKey(LiveChatSession, on_delete=models.CASCADE, related_name='messages', verbose_name='جلسة الدردشة')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المرسل')
    message = models.TextField(verbose_name='الرسالة')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='الطابع الزمني')
    is_read = models.BooleanField(default=False, verbose_name='مقروء')
    
    class Meta:
        verbose_name = 'رسالة دردشة مباشرة'
        verbose_name_plural = 'رسائل الدردشة المباشرة'
        ordering = ['timestamp']
    
    def __str__(self) -> str:
        sender_name = getattr(self.sender, 'username', 'Unknown User')
        return f"رسالة من {sender_name} في {self.timestamp}"

class SupportTicket(models.Model):
    """Model for customer support tickets"""
    PRIORITY_CHOICES = [
        ('low', 'منخفض'),
        ('medium', 'متوسط'),
        ('high', 'عالي'),
        ('urgent', 'عاجل'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'مفتوح'),
        ('in_progress', 'قيد المعالجة'),
        ('resolved', 'تم الحل'),
        ('closed', 'مغلق'),
        ('reopened', 'أُعيد فتحه'),
    ]
    
    CATEGORY_CHOICES = [
        ('technical', 'تقني'),
        ('billing', 'فوترة'),
        ('account', 'حساب'),
        ('product', 'منتج'),
        ('order', 'طلب'),
        ('other', 'أخرى'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets', verbose_name='العميل')
    assigned_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets', verbose_name='الوكيل المعين')
    subject = models.CharField(max_length=200, verbose_name='الموضوع')
    description = models.TextField(verbose_name='الوصف')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='الأولوية')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open', verbose_name='الحالة')
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='other', verbose_name='الفئة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الحل')
    attachment = models.FileField(upload_to='support_tickets/', null=True, blank=True, verbose_name='المرفق')
    
    class Meta:
        verbose_name = 'تذكرة دعم'
        verbose_name_plural = 'تذاكر الدعم'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        customer_name = getattr(self.customer, 'username', 'Unknown Customer')
        return f"تذكرة #{self.pk} - {customer_name} - {self.subject}"

class SupportTicketReply(models.Model):
    """Model for replies to support tickets"""
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='replies', verbose_name='التذكرة')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='الكاتب')
    message = models.TextField(verbose_name='الرسالة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    is_internal_note = models.BooleanField(default=False, verbose_name='ملاحظة داخلية')
    attachment = models.FileField(upload_to='support_ticket_replies/', null=True, blank=True, verbose_name='المرفق')
    
    class Meta:
        verbose_name = 'رد على تذكرة دعم'
        verbose_name_plural = 'ردود على تذاكر الدعم'
        ordering = ['created_at']
    
    def __str__(self) -> str:
        author_name = getattr(self.author, 'username', 'Unknown User')
        ticket_id = getattr(self.ticket, 'pk', 'Unknown')
        return f"رد من {author_name} على تذكرة #{ticket_id}"

class FAQCategory(models.Model):
    """Model for FAQ categories"""
    name = models.CharField(max_length=100, verbose_name='الاسم')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    order = models.PositiveIntegerField(default=0, verbose_name='الترتيب')
    is_active = models.BooleanField(default=True, verbose_name='مفعل')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'فئة الأسئلة الشائعة'
        verbose_name_plural = 'فئات الأسئلة الشائعة'
        ordering = ['order']
    
    def __str__(self) -> str:
        return str(self.name)

class FAQ(models.Model):
    """Model for frequently asked questions"""
    category = models.ForeignKey(FAQCategory, on_delete=models.CASCADE, related_name='faqs', verbose_name='الفئة')
    question = models.CharField(max_length=300, verbose_name='السؤال')
    answer = models.TextField(verbose_name='الإجابة')
    order = models.PositiveIntegerField(default=0, verbose_name='الترتيب')
    is_active = models.BooleanField(default=True, verbose_name='مفعل')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    views = models.PositiveIntegerField(default=0, verbose_name='المشاهدات')
    
    class Meta:
        verbose_name = 'سؤال شائع'
        verbose_name_plural = 'الأسئلة الشائعة'
        ordering = ['order']
    
    def __str__(self) -> str:
        return str(self.question)

# Enhanced Review Model
class EnhancedReview(models.Model):
    """Enhanced model for product reviews with additional features"""
    RATINGS = [
        (1, '1 - سيء'),
        (2, '2 - مقبول'),
        (3, '3 - جيد'),
        (4, '4 - جيد جداً'),
        (5, '5 - ممتاز'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='المنتج', related_name='enhanced_reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    rating = models.IntegerField(choices=RATINGS, verbose_name='التقييم')
    title = models.CharField(max_length=200, verbose_name='عنوان التقييم')
    comment = models.TextField(verbose_name='التعليق')
    pros = models.TextField(blank=True, null=True, verbose_name='الإيجابيات')
    cons = models.TextField(blank=True, null=True, verbose_name='السلبيات')
    is_verified_purchase = models.BooleanField(default=False, verbose_name='شراء مؤكد')
    is_featured = models.BooleanField(default=False, verbose_name='مميز')
    helpful_count = models.PositiveIntegerField(default=0, verbose_name='عدد المساعدين')
    not_helpful_count = models.PositiveIntegerField(default=0, verbose_name='عدد غير المساعدين')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'مراجعة محسنة'
        verbose_name_plural = 'مراجعات محسنة'
        unique_together = ('user', 'product')
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        username = getattr(self.user, 'username', 'Unknown User')
        return f"{username} - {self.product.name} - {self.rating}/5"
    
    @property
    def helpfulness_score(self) -> int:
        """Calculate helpfulness score"""
        total_votes = self.helpful_count + self.not_helpful_count
        if total_votes == 0:
            return 0
        return int((self.helpful_count / total_votes) * 100)

