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
        # Add more global currencies
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar'),
        ('CHF', 'Swiss Franc'),
        ('CNY', 'Chinese Yuan'),
        ('INR', 'Indian Rupee'),
        ('BRL', 'Brazilian Real'),
        ('MXN', 'Mexican Peso'),
        ('RUB', 'Russian Ruble'),
        ('SEK', 'Swedish Krona'),
        ('NOK', 'Norwegian Krone'),
        ('DKK', 'Danish Krone'),
        ('PLN', 'Polish Zloty'),
        ('TRY', 'Turkish Lira'),
        ('ZAR', 'South African Rand'),
        ('KRW', 'South Korean Won'),
        ('SGD', 'Singapore Dollar'),
        ('NZD', 'New Zealand Dollar'),
        ('HKD', 'Hong Kong Dollar'),
        ('THB', 'Thai Baht'),
        ('IDR', 'Indonesian Rupiah'),
        ('MYR', 'Malaysian Ringgit'),
        ('PHP', 'Philippine Peso'),
        ('VND', 'Vietnamese Dong'),
        ('CZK', 'Czech Koruna'),
        ('HUF', 'Hungarian Forint'),
        ('ILS', 'Israeli Shekel'),
        ('CLP', 'Chilean Peso'),
        ('COP', 'Colombian Peso'),
        ('PEN', 'Peruvian Sol'),
        ('ARS', 'Argentine Peso'),
        ('UYU', 'Uruguayan Peso'),
        ('PYG', 'Paraguayan Guarani'),
        ('BOB', 'Bolivian Boliviano'),
        ('CRC', 'Costa Rican Colón'),
        ('GTQ', 'Guatemalan Quetzal'),
        ('HNL', 'Honduran Lempira'),
        ('NIO', 'Nicaraguan Córdoba'),
        ('PAB', 'Panamanian Balboa'),
        ('DOP', 'Dominican Peso'),
        ('JMD', 'Jamaican Dollar'),
        ('TTD', 'Trinidad and Tobago Dollar'),
        ('BBD', 'Barbadian Dollar'),
        ('BSD', 'Bahamian Dollar'),
        ('BZD', 'Belize Dollar'),
        ('XCD', 'East Caribbean Dollar'),
        ('KYD', 'Cayman Islands Dollar'),
        # Additional global currencies
        ('AFN', 'Afghan Afghani'),
        ('ALL', 'Albanian Lek'),
        ('DZD', 'Algerian Dinar'),
        ('AOA', 'Angolan Kwanza'),
        ('AMD', 'Armenian Dram'),
        ('AWG', 'Aruban Florin'),
        ('AZN', 'Azerbaijani Manat'),
        ('BSD', 'Bahamian Dollar'),
        ('BDT', 'Bangladeshi Taka'),
        ('BBD', 'Barbadian Dollar'),
        ('BYN', 'Belarusian Ruble'),
        ('BZD', 'Belize Dollar'),
        ('BMD', 'Bermudian Dollar'),
        ('BTN', 'Bhutanese Ngultrum'),
        ('BOB', 'Bolivian Boliviano'),
        ('BAM', 'Bosnia and Herzegovina Convertible Mark'),
        ('BWP', 'Botswana Pula'),
        ('BND', 'Brunei Dollar'),
        ('BGN', 'Bulgarian Lev'),
        ('BIF', 'Burundian Franc'),
        ('KHR', 'Cambodian Riel'),
        ('CVE', 'Cape Verdean Escudo'),
        ('KYD', 'Cayman Islands Dollar'),
        ('XOF', 'CFA Franc BCEAO'),
        ('XAF', 'CFA Franc BEAC'),
        ('XPF', 'CFP Franc'),
        ('CLP', 'Chilean Peso'),
        ('CNY', 'Chinese Yuan'),
        ('COP', 'Colombian Peso'),
        ('KMF', 'Comorian Franc'),
        ('CDF', 'Congolese Franc'),
        ('CRC', 'Costa Rican Colón'),
        ('HRK', 'Croatian Kuna'),
        ('CUP', 'Cuban Peso'),
        ('CZK', 'Czech Koruna'),
        ('DKK', 'Danish Krone'),
        ('DJF', 'Djiboutian Franc'),
        ('DOP', 'Dominican Peso'),
        ('EGP', 'Egyptian Pound'),
        ('ERN', 'Eritrean Nakfa'),
        ('ETB', 'Ethiopian Birr'),
        ('EUR', 'Euro'),
        ('FKP', 'Falkland Islands Pound'),
        ('FJD', 'Fijian Dollar'),
        ('GMD', 'Gambian Dalasi'),
        ('GEL', 'Georgian Lari'),
        ('GHS', 'Ghanaian Cedi'),
        ('GIP', 'Gibraltar Pound'),
        ('GTQ', 'Guatemalan Quetzal'),
        ('GNF', 'Guinean Franc'),
        ('GYD', 'Guyanese Dollar'),
        ('HTG', 'Haitian Gourde'),
        ('HNL', 'Honduran Lempira'),
        ('HKD', 'Hong Kong Dollar'),
        ('HUF', 'Hungarian Forint'),
        ('ISK', 'Icelandic Króna'),
        ('INR', 'Indian Rupee'),
        ('IDR', 'Indonesian Rupiah'),
        ('IRR', 'Iranian Rial'),
        ('IQD', 'Iraqi Dinar'),
        ('ILS', 'Israeli New Shekel'),
        ('JMD', 'Jamaican Dollar'),
        ('JPY', 'Japanese Yen'),
        ('JOD', 'Jordanian Dinar'),
        ('KZT', 'Kazakhstani Tenge'),
        ('KES', 'Kenyan Shilling'),
        ('KPW', 'North Korean Won'),
        ('KRW', 'South Korean Won'),
        ('KWD', 'Kuwaiti Dinar'),
        ('KGS', 'Kyrgyzstani Som'),
        ('LAK', 'Lao Kip'),
        ('LBP', 'Lebanese Pound'),
        ('LSL', 'Lesotho Loti'),
        ('LRD', 'Liberian Dollar'),
        ('LYD', 'Libyan Dinar'),
        ('MOP', 'Macanese Pataca'),
        ('MKD', 'Macedonian Denar'),
        ('MGA', 'Malagasy Ariary'),
        ('MWK', 'Malawian Kwacha'),
        ('MYR', 'Malaysian Ringgit'),
        ('MVR', 'Maldivian Rufiyaa'),
        ('MRO', 'Mauritanian Ouguiya'),
        ('MUR', 'Mauritian Rupee'),
        ('MXN', 'Mexican Peso'),
        ('MDL', 'Moldovan Leu'),
        ('MNT', 'Mongolian Tögrög'),
        ('MAD', 'Moroccan Dirham'),
        ('MZN', 'Mozambican Metical'),
        ('MMK', 'Myanmar Kyat'),
        ('NAD', 'Namibian Dollar'),
        ('NPR', 'Nepalese Rupee'),
        ('ANG', 'Netherlands Antillean Guilder'),
        ('NZD', 'New Zealand Dollar'),
        ('NIO', 'Nicaraguan Córdoba'),
        ('NGN', 'Nigerian Naira'),
        ('NOK', 'Norwegian Krone'),
        ('OMR', 'Omani Rial'),
        ('PKR', 'Pakistani Rupee'),
        ('PAB', 'Panamanian Balboa'),
        ('PGK', 'Papua New Guinean Kina'),
        ('PYG', 'Paraguayan Guarani'),
        ('PEN', 'Peruvian Sol'),
        ('PHP', 'Philippine Peso'),
        ('PLN', 'Polish Złoty'),
        ('QAR', 'Qatari Riyal'),
        ('RON', 'Romanian Leu'),
        ('RUB', 'Russian Ruble'),
        ('RWF', 'Rwandan Franc'),
        ('SHP', 'Saint Helena Pound'),
        ('WST', 'Samoan Tala'),
        ('STN', 'São Tomé and Príncipe Dobra'),
        ('SAR', 'Saudi Riyal'),
        ('RSD', 'Serbian Dinar'),
        ('SCR', 'Seychellois Rupee'),
        ('SLL', 'Sierra Leonean Leone'),
        ('SGD', 'Singapore Dollar'),
        ('SBD', 'Solomon Islands Dollar'),
        ('SOS', 'Somali Shilling'),
        ('ZAR', 'South African Rand'),
        ('SSP', 'South Sudanese Pound'),
        ('LKR', 'Sri Lankan Rupee'),
        ('SDG', 'Sudanese Pound'),
        ('SRD', 'Surinamese Dollar'),
        ('SZL', 'Swazi Lilangeni'),
        ('SEK', 'Swedish Krona'),
        ('CHF', 'Swiss Franc'),
        ('SYP', 'Syrian Pound'),
        ('TWD', 'New Taiwan Dollar'),
        ('TJS', 'Tajikistani Somoni'),
        ('TZS', 'Tanzanian Shilling'),
        ('THB', 'Thai Baht'),
        ('TOP', 'Tongan Paʻanga'),
        ('TTD', 'Trinidad and Tobago Dollar'),
        ('TND', 'Tunisian Dinar'),
        ('TRY', 'Turkish Lira'),
        ('TMT', 'Turkmenistani Manat'),
        ('UGX', 'Ugandan Shilling'),
        ('UAH', 'Ukrainian Hryvnia'),
        ('AED', 'United Arab Emirates Dirham'),
        ('USD', 'United States Dollar'),
        ('UYU', 'Uruguayan Peso'),
        ('UZS', 'Uzbekistani Som'),
        ('VUV', 'Vanuatu Vatu'),
        ('VES', 'Venezuelan Bolívar'),
        ('VND', 'Vietnamese Đồng'),
        ('YER', 'Yemeni Rial'),
        ('ZMW', 'Zambian Kwacha'),
        ('ZWL', 'Zimbabwean Dollar'),
    ]

    name = models.CharField(max_length=100, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    description = models.TextField(blank=True, default="لا يوجد وصف")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='phones', db_index=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD', verbose_name='العملة', db_index=True)
    
    # Add seller field for multi-vendor support
    seller = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='البائع', null=True, blank=True)
    
    # Add inventory management fields
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name='كمية المخزون')  # type: ignore
    low_stock_threshold = models.PositiveIntegerField(default=5, verbose_name='حد التنبيه عند انخفاض المخزون')  # type: ignore
    
    # SEO fields with internationalization support
    seo_title = models.CharField(max_length=60, blank=True, verbose_name="عنوان SEO", db_index=True)
    seo_description = models.CharField(max_length=160, blank=True, verbose_name="وصف SEO", db_index=True)
    seo_keywords = models.CharField(max_length=255, blank=True, verbose_name="كلمات مفتاحية SEO", db_index=True)
    
    # Add internationalization fields
    name_en = models.CharField(max_length=100, blank=True, null=True, verbose_name="Product Name (English)")
    description_en = models.TextField(blank=True, null=True, verbose_name="Description (English)")
    seo_title_en = models.CharField(max_length=60, blank=True, null=True, verbose_name="SEO Title (English)")
    seo_description_en = models.CharField(max_length=160, blank=True, null=True, verbose_name="SEO Description (English)")
    seo_keywords_en = models.CharField(max_length=255, blank=True, null=True, verbose_name="SEO Keywords (English)")

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
    
    # Get image URLs for responsive images
    def get_responsive_image_urls(self):
        if not self.image:
            return None
        
        # Return URLs for different image sizes
        try:
            # Access image URL safely
            image_field = getattr(self, 'image', None)
            if image_field and hasattr(image_field, 'url'):
                image_url = image_field.url
                return {
                    'small': image_url,
                    'medium': image_url,
                    'large': image_url,
                    'webp': image_url.replace('.', '.webp') if image_url else None
                }
        except Exception:
            pass
        return None


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
            username = getattr(self.user, 'username', 'Unknown User')
            role_display = getattr(self, 'get_role_display', lambda: 'Unknown')()
            return f"{username} - {role_display}"
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

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم', null=True, blank=True)
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
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['user', 'status']),
        ]

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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم', null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='الطلب', null=True, blank=True)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, verbose_name='نوع الإشعار')
    message = models.TextField(verbose_name='الرسالة')
    is_read = models.BooleanField(default=False, verbose_name='مقروء')  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_read', '-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
        ]
    
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
    is_paid = models.BooleanField(default=False, verbose_name='تم الدفع')  # type: ignore
    
    class Meta:
        verbose_name = 'عمولة'
        verbose_name_plural = 'العمولات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['order', '-created_at']),
            models.Index(fields=['is_paid', '-created_at']),
        ]
    
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
    is_active = models.BooleanField(default=True, verbose_name='مفعل')  # type: ignore
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
        # Add more global payment methods
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
        ('amazon_pay', 'Amazon Pay'),
        ('klarna', 'Klarna'),
        ('afterpay', 'Afterpay'),
        ('alipay', 'Alipay'),
        ('wechat_pay', 'WeChat Pay'),
        ('ideal', 'iDEAL'),
        ('sofort', 'SOFORT'),
        ('giropay', 'Giropay'),
        ('bancontact', 'Bancontact'),
        ('eps', 'EPS'),
        ('przelewy24', 'Przelewy24'),
        ('multibanco', 'Multibanco'),
        ('sepa_debit', 'SEPA Direct Debit'),
        ('boleto', 'Boleto Bancário'),  # Brazil
        ('oxxo', 'OXXO'),  # Mexico
        ('konbini', 'Konbini'),  # Japan
        ('alipay_hk', 'Alipay HK'),  # Hong Kong
        ('gcash', 'GCash'),  # Philippines
        ('dana', 'DANA'),  # Indonesia
        ('kakao_pay', 'Kakao Pay'),  # South Korea
        ('toss', 'Toss'),  # South Korea
        ('paytm', 'Paytm'),  # India
        ('phonepe', 'PhonePe'),  # India
        ('upi', 'UPI'),  # India
        ('pix', 'PIX'),  # Brazil
        ('mb_way', 'MB WAY'),  # Portugal
        ('blik', 'BLIK'),  # Poland
        ('trustly', 'Trustly'),  # Europe
        ('verkkopankki', 'Verkkopankki'),  # Finland
        ('swish', 'Swish'),  # Sweden
        ('vipps', 'Vipps'),  # Norway
        ('mobilepay', 'MobilePay'),  # Denmark
        ('twint', 'TWINT'),  # Switzerland
        ('payconiq', 'Payconiq'),  # Belgium
        ('satispay', 'Satispay'),  # Italy
        ('mybank', 'MyBank'),  # Italy
        ('belfius', 'Belfius'),  # Belgium
        ('ing_home_pay', 'ING Home\'Pay'),  # Belgium
        ('kbc', 'KBC'),  # Belgium
        # Additional global payment methods
        ('unionpay', 'UnionPay'),  # China
        ('jcb', 'JCB'),  # Japan
        ('diners_club', 'Diners Club'),  # Global
        ('discover', 'Discover'),  # US
        ('american_express', 'American Express'),  # Global
        ('mastercard', 'Mastercard'),  # Global
        ('visa', 'Visa'),  # Global
        ('maestro', 'Maestro'),  # Europe
        ('solo', 'Solo'),  # UK
        ('laser', 'Laser'),  # Ireland
        ('switch', 'Switch'),  # UK
        ('delta', 'Delta'),  # UK
        ('electron', 'Electron'),  # Global
        ('cirrus', 'Cirrus'),  # Global
        ('paypal_credit', 'PayPal Credit'),  # Global
        ('paypal_express', 'PayPal Express'),  # Global
        ('paypal_pro', 'PayPal Pro'),  # Global
        ('amazon_payments', 'Amazon Payments'),  # Global
        ('amazon_checkout', 'Amazon Checkout'),  # Global
        ('google_checkout', 'Google Checkout'),  # Global
        ('google_wallet', 'Google Wallet'),  # Global
        ('samsung_pay', 'Samsung Pay'),  # Global
        ('android_pay', 'Android Pay'),  # Global
        ('microsoft_pay', 'Microsoft Pay'),  # Global
        ('facebook_pay', 'Facebook Pay'),  # Global
        ('snapchat_pay', 'Snapchat Pay'),  # Global
        ('instagram_pay', 'Instagram Pay'),  # Global
        ('twitter_pay', 'Twitter Pay'),  # Global
        ('linkedin_pay', 'LinkedIn Pay'),  # Global
        ('pinterest_pay', 'Pinterest Pay'),  # Global
        ('tiktok_pay', 'TikTok Pay'),  # Global
        ('youtube_pay', 'YouTube Pay'),  # Global
        ('reddit_pay', 'Reddit Pay'),  # Global
        ('discord_pay', 'Discord Pay'),  # Global
        ('twitch_pay', 'Twitch Pay'),  # Global
        ('wechat_wallet', 'WeChat Wallet'),  # China
        ('alipay_wallet', 'Alipay Wallet'),  # China
        ('tenpay', 'Tenpay'),  # China
        ('baidu_wallet', 'Baidu Wallet'),  # China
        ('qq_wallet', 'QQ Wallet'),  # China
        ('jd_pay', 'JD Pay'),  # China
        ('ali_pay', 'Ali Pay'),  # China
        ('kuaiqian', 'Kuaiqian'),  # China
        ('yeepay', 'Yeepay'),  # China
        ('billdesk', 'BillDesk'),  # India
        ('ccavenue', 'CCAvenue'),  # India
        ('payu', 'PayU'),  # India/Global
        ('razorpay', 'Razorpay'),  # India
        ('instamojo', 'Instamojo'),  # India
        ('cashfree', 'Cashfree'),  # India
        ('paykun', 'PayKun'),  # India
        ('easebuzz', 'Easebuzz'),  # India
        ('atom', 'Atom'),  # India
        ('payza', 'Payza'),  # Global
        ('skrill', 'Skrill'),  # Global
        ('neteller', 'Neteller'),  # Global
        ('webmoney', 'WebMoney'),  # Global
        ('qiwi', 'Qiwi'),  # Russia
        ('yandex_money', 'Yandex.Money'),  # Russia
        ('webpay', 'WebPay'),  # Belarus
        ('epay', 'ePay'),  # Bulgaria
        ('dotpay', 'Dotpay'),  # Poland
        ('tinkoff', 'Tinkoff'),  # Russia
        ('alfabank', 'Alfa-Bank'),  # Russia
        ('sberbank', 'Sberbank'),  # Russia
        ('vtb', 'VTB'),  # Russia
        ('gazprombank', 'Gazprombank'),  # Russia
        ('raiffeisen', 'Raiffeisen'),  # Russia
        ('promsvyazbank', 'Promsvyazbank'),  # Russia
        ('rosbank', 'Rosbank'),  # Russia
        ('uralsib', 'Uralsib'),  # Russia
        ('rshb', 'Russian Agricultural Bank'),  # Russia
        ('home_credit', 'Home Credit'),  # Russia
        ('mkb', 'Moscow Credit Bank'),  # Russia
        ('novikom', 'Novikom'),  # Russia
        ('petrocommerce', 'Petrocommerce'),  # Russia
        ('metallinvestbank', 'Metallinvestbank'),  # Russia
        ('binbank', 'Binbank'),  # Russia
        ('avangard', 'Avangard'),  # Russia
        ('zenit', 'Zenit'),  # Russia
        ('open', 'Open'),  # Russia
        ('otp', 'OTP'),  # Hungary
        ('erste', 'Erste'),  # Hungary
        ('unicredit', 'UniCredit'),  # Hungary
        ('mkb', 'MKB'),  # Hungary
        ('cib', 'CIB'),  # Hungary
        ('kh', 'K&amp;H'),  # Hungary
        ('takarek', 'Takarek'),  # Hungary
        ('sopron', 'Sopron'),  # Hungary
        ('oberbank', 'Oberbank'),  # Hungary
        ('raiffeisen_hungary', 'Raiffeisen Hungary'),  # Hungary
        ('otp_hungary', 'OTP Hungary'),  # Hungary
        ('erste_hungary', 'Erste Hungary'),  # Hungary
        ('unicredit_hungary', 'UniCredit Hungary'),  # Hungary
        ('mkb_hungary', 'MKB Hungary'),  # Hungary
        ('cib_hungary', 'CIB Hungary'),  # Hungary
        ('kh_hungary', 'K&amp;H Hungary'),  # Hungary
        ('takarek_hungary', 'Takarek Hungary'),  # Hungary
        ('sopron_hungary', 'Sopron Hungary'),  # Hungary
        ('oberbank_hungary', 'Oberbank Hungary'),  # Hungary
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
        # Add more global currencies
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar'),
        ('CHF', 'Swiss Franc'),
        ('CNY', 'Chinese Yuan'),
        ('INR', 'Indian Rupee'),
        ('BRL', 'Brazilian Real'),
        ('MXN', 'Mexican Peso'),
        ('RUB', 'Russian Ruble'),
        ('SEK', 'Swedish Krona'),
        ('NOK', 'Norwegian Krone'),
        ('DKK', 'Danish Krone'),
        ('PLN', 'Polish Zloty'),
        ('TRY', 'Turkish Lira'),
        ('ZAR', 'South African Rand'),
        ('KRW', 'South Korean Won'),
        ('SGD', 'Singapore Dollar'),
        ('NZD', 'New Zealand Dollar'),
        ('HKD', 'Hong Kong Dollar'),
        ('THB', 'Thai Baht'),
        ('IDR', 'Indonesian Rupiah'),
        ('MYR', 'Malaysian Ringgit'),
        ('PHP', 'Philippine Peso'),
        ('VND', 'Vietnamese Dong'),
        ('CZK', 'Czech Koruna'),
        ('HUF', 'Hungarian Forint'),
        ('ILS', 'Israeli Shekel'),
        ('CLP', 'Chilean Peso'),
        ('COP', 'Colombian Peso'),
        ('PEN', 'Peruvian Sol'),
        ('ARS', 'Argentine Peso'),
        ('UYU', 'Uruguayan Peso'),
        ('PYG', 'Paraguayan Guarani'),
        ('BOB', 'Bolivian Boliviano'),
        ('CRC', 'Costa Rican Colón'),
        ('GTQ', 'Guatemalan Quetzal'),
        ('HNL', 'Honduran Lempira'),
        ('NIO', 'Nicaraguan Córdoba'),
        ('PAB', 'Panamanian Balboa'),
        ('DOP', 'Dominican Peso'),
        ('JMD', 'Jamaican Dollar'),
        ('TTD', 'Trinidad and Tobago Dollar'),
        ('BBD', 'Barbadian Dollar'),
        ('BSD', 'Bahamian Dollar'),
        ('BZD', 'Belize Dollar'),
        ('XCD', 'East Caribbean Dollar'),
        ('KYD', 'Cayman Islands Dollar'),
        ('BMD', 'Bermudian Dollar'),
        ('BAM', 'Bosnia and Herzegovina Convertible Mark'),
        ('BGN', 'Bulgarian Lev'),
        ('HRK', 'Croatian Kuna'),
        ('CZK', 'Czech Koruna'),
        ('GEL', 'Georgian Lari'),
        ('ISK', 'Icelandic Króna'),
        ('KZT', 'Kazakhstani Tenge'),
        ('MKD', 'Macedonian Denar'),
        ('MDL', 'Moldovan Leu'),
        ('RSD', 'Serbian Dinar'),
        ('UAH', 'Ukrainian Hryvnia'),
        ('UZS', 'Uzbekistani Som'),
        ('AZN', 'Azerbaijani Manat'),
        ('AMD', 'Armenian Dram'),
        ('BYN', 'Belarusian Ruble'),
        ('KGS', 'Kyrgyzstani Som'),
        ('TJS', 'Tajikistani Somoni'),
        ('TMT', 'Turkmenistani Manat'),
        ('UZS', 'Uzbekistani Som'),
        ('GHS', 'Ghanaian Cedi'),
        ('NGN', 'Nigerian Naira'),
        ('KES', 'Kenyan Shilling'),
        ('UGX', 'Ugandan Shilling'),
        ('TZS', 'Tanzanian Shilling'),
        ('RWF', 'Rwandan Franc'),
        ('BWP', 'Botswana Pula'),
        ('ZMW', 'Zambian Kwacha'),
        ('MWK', 'Malawian Kwacha'),
        ('MUR', 'Mauritian Rupee'),
        ('SCR', 'Seychellois Rupee'),
        ('MZN', 'Mozambican Metical'),
        ('AOA', 'Angolan Kwanza'),
        ('CDF', 'Congolese Franc'),
        ('XOF', 'West African CFA Franc'),
        ('XAF', 'Central African CFA Franc'),
        ('DJF', 'Djiboutian Franc'),
        ('ERN', 'Eritrean Nakfa'),
        ('ETB', 'Ethiopian Birr'),
        ('GMD', 'Gambian Dalasi'),
        ('GNF', 'Guinean Franc'),
        ('LSL', 'Lesotho Loti'),
        ('LRD', 'Liberian Dollar'),
        ('LYD', 'Libyan Dinar'),
        ('MGA', 'Malagasy Ariary'),
        ('MRO', 'Mauritanian Ouguiya'),
        ('MVR', 'Maldivian Rufiyaa'),
        ('MRU', 'Mauritanian Ouguiya'),
        ('NAD', 'Namibian Dollar'),
        ('PGK', 'Papua New Guinean Kina'),
        ('PEN', 'Peruvian Sol'),
        ('SBD', 'Solomon Islands Dollar'),
        ('SLL', 'Sierra Leonean Leone'),
        ('SOS', 'Somali Shilling'),
        ('SRD', 'Surinamese Dollar'),
        ('STD', 'São Tomé and Príncipe Dobra'),
        ('STN', 'São Tomé and Príncipe Dobra'),
        ('SZL', 'Swazi Lilangeni'),
        ('TND', 'Tunisian Dinar'),
        ('TOP', 'Tongan Paʻanga'),
        ('VES', 'Venezuelan Bolívar'),
        ('VUV', 'Vanuatu Vatu'),
        ('WST', 'Samoan Tala'),
        ('XPF', 'CFP Franc'),
        ('YER', 'Yemeni Rial'),
        ('ZWL', 'Zimbabwean Dollar'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name='الطلب')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, verbose_name='طريقة الدفع')
    transaction_id = models.CharField(max_length=100, unique=True, verbose_name='معرف المعاملة')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='المبلغ')
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
    # Add more specific tax types for global support
    TAX_TYPES = [
        ('vat', 'VAT (Value Added Tax)'),
        ('gst', 'GST (Goods and Services Tax)'),
        ('sales_tax', 'Sales Tax'),
        ('customs_duty', 'Customs Duty'),
        ('excise_tax', 'Excise Tax'),
        ('service_tax', 'Service Tax'),
        ('luxury_tax', 'Luxury Tax'),
        ('import_tax', 'Import Tax'),
        ('export_tax', 'Export Tax'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='اسم الضريبة')
    tax_type = models.CharField(max_length=20, choices=TAX_TYPES, default='vat', verbose_name='نوع الضريبة')
    rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='نسبة الضريبة (%)')
    country_code = models.CharField(max_length=2, blank=True, null=True, verbose_name='رمز البلد (ISO 3166-1 alpha-2)')
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name='المنطقة/الولاية')
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name='الرمز البريدي')
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
        # Add more global advertising platforms
        ('linkedin', 'LinkedIn'),
        ('pinterest', 'Pinterest'),
        ('tiktok', 'TikTok'),
        ('snapchat', 'Snapchat'),
        ('youtube', 'YouTube'),
        ('reddit', 'Reddit'),
        ('quora', 'Quora'),
        ('taboola', 'Taboola'),
        ('outbrain', 'Outbrain'),
        ('adroll', 'AdRoll'),
        ('bing_ads', 'Bing Ads'),
        ('yahoo_gemini', 'Yahoo Gemini'),
        ('amazon_ads', 'Amazon Ads'),
        ('ebay_ads', 'eBay Ads'),
        ('criteo', 'Criteo'),
        ('adwords', 'Google AdWords'),
        ('admob', 'Google AdMob'),
        ('doubleclick', 'Google DoubleClick'),
        ('facebook_audience_network', 'Facebook Audience Network'),
        ('instagram_stories', 'Instagram Stories'),
        ('instagram_reels', 'Instagram Reels'),
        ('facebook_messenger', 'Facebook Messenger'),
        ('whatsapp_business', 'WhatsApp Business'),
        ('twitter_ads', 'Twitter Ads'),
        ('linkedin_ads', 'LinkedIn Ads'),
        ('pinterest_ads', 'Pinterest Ads'),
        ('snapchat_ads', 'Snapchat Ads'),
        ('tiktok_ads', 'TikTok Ads'),
        ('youtube_ads', 'YouTube Ads'),
        ('reddit_ads', 'Reddit Ads'),
        ('quora_ads', 'Quora Ads'),
        ('taboola_ads', 'Taboola Ads'),
        ('outbrain_ads', 'Outbrain Ads'),
        ('adroll_ads', 'AdRoll Ads'),
        ('yahoo_gemini_ads', 'Yahoo Gemini Ads'),
        ('amazon_advertising', 'Amazon Advertising'),
        ('ebay_advertising', 'eBay Advertising'),
        ('criteo_ads', 'Criteo Ads'),
        ('taboola_advertising', 'Taboola Advertising'),
        ('outbrain_advertising', 'Outbrain Advertising'),
        ('taboola_marketing', 'Taboola Marketing'),
        ('outbrain_marketing', 'Outbrain Marketing'),
        ('adwords_express', 'Google AdWords Express'),
        ('admob_express', 'Google AdMob Express'),
        ('doubleclick_dfp', 'Google DoubleClick DFP'),
        ('facebook_instagram_ads', 'Facebook & Instagram Ads'),
        ('messenger_ads', 'Messenger Ads'),
        ('whatsapp_promotions', 'WhatsApp Promotions'),
        ('twitter_promoted_tweets', 'Twitter Promoted Tweets'),
        ('linkedin_sponsored_content', 'LinkedIn Sponsored Content'),
        ('pinterest_promoted_pins', 'Pinterest Promoted Pins'),
        ('snapchat_sponsored_lens', 'Snapchat Sponsored Lens'),
        ('tiktok_branded_content', 'TikTok Branded Content'),
        ('youtube_promoted_videos', 'YouTube Promoted Videos'),
        ('reddit_promoted_posts', 'Reddit Promoted Posts'),
        ('quora_ads_platform', 'Quora Ads Platform'),
        # Additional global platforms
        ('spotify_ads', 'Spotify Ads'),
        ('pandora_ads', 'Pandora Ads'),
        ('applovin', 'AppLovin'),
        ('unity_ads', 'Unity Ads'),
        ('vungle', 'Vungle'),
        ('chartboost', 'Chartboost'),
        ('adcolony', 'AdColony'),
        ('inmobi', 'InMobi'),
        ('mopub', 'MoPub'),
        ('smaato', 'Smaato'),
        ('pubmatic', 'PubMatic'),
        ('openx', 'OpenX'),
        ('rubicon_project', 'Rubicon Project'),
        ('the_trade_desk', 'The Trade Desk'),
        ('appnexus', 'AppNexus'),
        ('index_exchange', 'Index Exchange'),
        ('sovrn', 'Sovrn'),
        ('pulsepoint', 'PulsePoint'),
        ('district_m', 'District M'),
        ('gumgum', 'GumGum'),
        ('sonobi', 'Sonobi'),
        ('yieldmo', 'Yieldmo'),
        ('revcontent', 'RevContent'),
        ('mgid', 'MGID'),
        ('zemanta', 'Zemanta'),
        ('content_ad', 'Content.ad'),
        ('outbrain_amp', 'Outbrain AMP'),
        ('taboola_amp', 'Taboola AMP'),
        ('google_adsense', 'Google AdSense'),
        ('media_net', 'Media.net'),
        ('propeller_ads', 'Propeller Ads'),
        ('exoclick', 'ExoClick'),
        ('popads', 'PopAds'),
        ('adsterra', 'Adsterra'),
        ('traffic_stars', 'Traffic Stars'),
        ('adult_webmaster_empire', 'Adult Webmaster Empire'),
        ('clickbank', 'ClickBank'),
        ('shareasale', 'ShareASale'),
        ('cj_affiliate', 'CJ Affiliate'),
        ('amazon_associates', 'Amazon Associates'),
        ('ebay_partner_network', 'eBay Partner Network'),
        ('google_affiliate_network', 'Google Affiliate Network'),
        ('facebook_affiliate', 'Facebook Affiliate'),
        ('instagram_affiliate', 'Instagram Affiliate'),
        ('twitter_affiliate', 'Twitter Affiliate'),
        ('linkedin_affiliate', 'LinkedIn Affiliate'),
        ('pinterest_affiliate', 'Pinterest Affiliate'),
        ('tiktok_affiliate', 'TikTok Affiliate'),
        ('youtube_affiliate', 'YouTube Affiliate'),
        ('snapchat_affiliate', 'Snapchat Affiliate'),
        ('reddit_affiliate', 'Reddit Affiliate'),
        ('quora_affiliate', 'Quora Affiliate'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='اسم الحملة')
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, verbose_name='المنصة')
    budget = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='الميزانية')
    spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='المنفق')
    clicks = models.PositiveIntegerField(default=0, verbose_name='النقرات')  # type: ignore
    impressions = models.PositiveIntegerField(default=0, verbose_name='الظهور')  # type: ignore
    conversions = models.PositiveIntegerField(default=0, verbose_name='التحويلات')  # type: ignore
    start_date = models.DateTimeField(verbose_name='تاريخ البدء')
    end_date = models.DateTimeField(verbose_name='تاريخ الانتهاء')
    active = models.BooleanField(default=True, verbose_name='مفعل')  # type: ignore
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
        # Add more global social media platforms
        ('tiktok', 'TikTok'),
        ('youtube', 'YouTube'),
        ('snapchat', 'Snapchat'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('reddit', 'Reddit'),
        ('discord', 'Discord'),
        ('twitch', 'Twitch'),
        ('wechat', 'WeChat'),
        ('qq', 'QQ'),
        ('weibo', 'Weibo'),
        ('douyin', 'Douyin'),
        ('kakao', 'KakaoTalk'),
        ('line', 'LINE'),
        ('viber', 'Viber'),
        ('skype', 'Skype'),
        ('clubhouse', 'Clubhouse'),
        ('bebo', 'Bebo'),
        ('myspace', 'MySpace'),
        ('flickr', 'Flickr'),
        ('tumblr', 'Tumblr'),
        ('quora', 'Quora'),
        ('xing', 'Xing'),
        ('mix', 'Mix'),
        ('meetup', 'Meetup'),
        ('nextdoor', 'Nextdoor'),
        ('tagged', 'Tagged'),
        ('hi5', 'Hi5'),
        ('renren', 'Renren'),
        ('kaixin', 'Kaixin'),
        ('vkontakte', 'VKontakte'),
        ('odnoklassniki', 'Odnoklassniki'),
        ('livejournal', 'LiveJournal'),
        ('blogger', 'Blogger'),
        ('medium', 'Medium'),
        ('deviantart', 'DeviantArt'),
        ('behance', 'Behance'),
        ('dribbble', 'Dribbble'),
        ('ello', 'Ello'),
        ('mastodon', 'Mastodon'),
        ('pleroma', 'Pleroma'),
        ('misskey', 'Misskey'),
        ('pixelfed', 'Pixelfed'),
        ('peertube', 'PeerTube'),
        ('diaspora', 'Diaspora'),
        ('friendica', 'Friendica'),
        ('hubzilla', 'Hubzilla'),
        ('movim', 'Movim'),
        ('socialhome', 'Socialhome'),
        ('ganggo', 'GangGo'),
        ('prismo', 'Prismo'),
        ('lemmy', 'Lemmy'),
        ('kbin', 'Kbin'),
        ('threads', 'Threads'),
        # Additional global social media platforms
        ('snapchat_business', 'Snapchat Business'),
        ('linkedin_business', 'LinkedIn Business'),
        ('pinterest_business', 'Pinterest Business'),
        ('tiktok_business', 'TikTok Business'),
        ('youtube_business', 'YouTube Business'),
        ('reddit_business', 'Reddit Business'),
        ('quora_business', 'Quora Business'),
        ('tumblr_business', 'Tumblr Business'),
        ('flickr_business', 'Flickr Business'),
        ('myspace_business', 'MySpace Business'),
        ('bebo_business', 'Bebo Business'),
        ('hi5_business', 'Hi5 Business'),
        ('tagged_business', 'Tagged Business'),
        ('nextdoor_business', 'Nextdoor Business'),
        ('meetup_business', 'Meetup Business'),
        ('mix_business', 'Mix Business'),
        ('xing_business', 'Xing Business'),
        ('blogger_business', 'Blogger Business'),
        ('medium_business', 'Medium Business'),
        ('deviantart_business', 'DeviantArt Business'),
        ('behance_business', 'Behance Business'),
        ('dribbble_business', 'Dribbble Business'),
        ('ello_business', 'Ello Business'),
        ('mastodon_business', 'Mastodon Business'),
        ('pleroma_business', 'Pleroma Business'),
        ('misskey_business', 'Misskey Business'),
        ('pixelfed_business', 'Pixelfed Business'),
        ('peertube_business', 'PeerTube Business'),
        ('diaspora_business', 'Diaspora Business'),
        ('friendica_business', 'Friendica Business'),
        ('hubzilla_business', 'Hubzilla Business'),
        ('movim_business', 'Movim Business'),
        ('socialhome_business', 'Socialhome Business'),
        ('ganggo_business', 'GangGo Business'),
        ('prismo_business', 'Prismo Business'),
        ('lemmy_business', 'Lemmy Business'),
        ('kbin_business', 'Kbin Business'),
        ('threads_business', 'Threads Business'),
        ('wechat_business', 'WeChat Business'),
        ('qq_business', 'QQ Business'),
        ('weibo_business', 'Weibo Business'),
        ('douyin_business', 'Douyin Business'),
        ('kakao_business', 'KakaoTalk Business'),
        ('line_business', 'LINE Business'),
        ('viber_business', 'Viber Business'),
        ('skype_business', 'Skype Business'),
        ('clubhouse_business', 'Clubhouse Business'),
        ('renren_business', 'Renren Business'),
        ('kaixin_business', 'Kaixin Business'),
        ('vkontakte_business', 'VKontakte Business'),
        ('odnoklassniki_business', 'Odnoklassniki Business'),
        ('livejournal_business', 'LiveJournal Business'),
        ('telegram_business', 'Telegram Business'),
        ('whatsapp_business', 'WhatsApp Business'),
        ('discord_business', 'Discord Business'),
        ('twitch_business', 'Twitch Business'),
        ('snapchat_ads', 'Snapchat Ads'),
        ('linkedin_ads', 'LinkedIn Ads'),
        ('pinterest_ads', 'Pinterest Ads'),
        ('tiktok_ads', 'TikTok Ads'),
        ('youtube_ads', 'YouTube Ads'),
        ('reddit_ads', 'Reddit Ads'),
        ('quora_ads', 'Quora Ads'),
        ('tumblr_ads', 'Tumblr Ads'),
        ('flickr_ads', 'Flickr Ads'),
        ('myspace_ads', 'MySpace Ads'),
        ('bebo_ads', 'Bebo Ads'),
        ('hi5_ads', 'Hi5 Ads'),
        ('tagged_ads', 'Tagged Ads'),
        ('nextdoor_ads', 'Nextdoor Ads'),
        ('meetup_ads', 'Meetup Ads'),
        ('mix_ads', 'Mix Ads'),
        ('xing_ads', 'Xing Ads'),
        ('blogger_ads', 'Blogger Ads'),
        ('medium_ads', 'Medium Ads'),
        ('deviantart_ads', 'DeviantArt Ads'),
        ('behance_ads', 'Behance Ads'),
        ('dribbble_ads', 'Dribbble Ads'),
        ('ello_ads', 'Ello Ads'),
        ('mastodon_ads', 'Mastodon Ads'),
        ('pleroma_ads', 'Pleroma Ads'),
        ('misskey_ads', 'Misskey Ads'),
        ('pixelfed_ads', 'Pixelfed Ads'),
        ('peertube_ads', 'PeerTube Ads'),
        ('diaspora_ads', 'Diaspora Ads'),
        ('friendica_ads', 'Friendica Ads'),
        ('hubzilla_ads', 'Hubzilla Ads'),
        ('movim_ads', 'Movim Ads'),
        ('socialhome_ads', 'Socialhome Ads'),
        ('ganggo_ads', 'GangGo Ads'),
        ('prismo_ads', 'Prismo Ads'),
        ('lemmy_ads', 'Lemmy Ads'),
        ('kbin_ads', 'Kbin Ads'),
        ('threads_ads', 'Threads Ads'),
        ('wechat_ads', 'WeChat Ads'),
        ('qq_ads', 'QQ Ads'),
        ('weibo_ads', 'Weibo Ads'),
        ('douyin_ads', 'Douyin Ads'),
        ('kakao_ads', 'KakaoTalk Ads'),
        ('line_ads', 'LINE Ads'),
        ('viber_ads', 'Viber Ads'),
        ('skype_ads', 'Skype Ads'),
        ('clubhouse_ads', 'Clubhouse Ads'),
        ('renren_ads', 'Renren Ads'),
        ('kaixin_ads', 'Kaixin Ads'),
        ('vkontakte_ads', 'VKontakte Ads'),
        ('odnoklassniki_ads', 'Odnoklassniki Ads'),
        ('livejournal_ads', 'LiveJournal Ads'),
        ('telegram_ads', 'Telegram Ads'),
        ('whatsapp_ads', 'WhatsApp Ads'),
        ('discord_ads', 'Discord Ads'),
        ('twitch_ads', 'Twitch Ads'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='المنتج')
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, verbose_name='المنصة')
    post_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='معرف المنشور')
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name='مجدول في')
    posted_at = models.DateTimeField(null=True, blank=True, verbose_name='نُشر في')
    status = models.CharField(max_length=20, default='pending', verbose_name='الحالة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'تكامل وسائل التواصل'
        verbose_name_plural = 'تكاملات وسائل التواصل'
        unique_together = ('product', 'platform')
    
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
        ('dhl_express', 'DHL Express'),  # Add for global shipping
        ('ups_worldwide', 'UPS Worldwide'),  # Add for global shipping
        ('fedex_international', 'FedEx International'),  # Add for global shipping
        ('usps', 'USPS'),  # Add for US shipping
        ('royal_mail', 'Royal Mail'),  # Add for UK shipping
        ('australia_post', 'Australia Post'),  # Add for Australia shipping
        ('canada_post', 'Canada Post'),  # Add for Canada shipping
        ('correos', 'Correos'),  # Add for Spain shipping
        ('poste_italiane', 'Poste Italiane'),  # Add for Italy shipping
        ('deutsche_post', 'Deutsche Post'),  # Add for Germany shipping
        ('la_poste', 'La Poste'),  # Add for France shipping
        ('japan_post', 'Japan Post'),  # Add for Japan shipping
        ('singapore_post', 'Singapore Post'),  # Add for Singapore shipping
        ('korea_post', 'Korea Post'),  # Add for South Korea shipping
        ('china_post', 'China Post'),  # Add for China shipping
        ('india_post', 'India Post'),  # Add for India shipping
        ('brazil_correios', 'Brazil Correios'),  # Add for Brazil shipping
        ('mexico_post', 'Mexico Post'),  # Add for Mexico shipping
        ('russian_post', 'Russian Post'),  # Add for Russia shipping
        # Additional global shipping providers
        ('purolator', 'Purolator'),  # Canada
        ('chronopost', 'Chronopost'),  # France
        ('dpd', 'DPD'),  # Europe
        ('gls', 'GLS'),  # Europe
        ('tnt', 'TNT'),  # Global
        ('ups_freight', 'UPS Freight'),  # Global
        ('fedex_freight', 'FedEx Freight'),  # Global
        ('dhl_freight', 'DHL Freight'),  # Global
        ('yamato', 'Yamato Transport'),  # Japan
        ('sagawa', 'Sagawa Express'),  # Japan
        ('postnl', 'PostNL'),  # Netherlands
        ('poste_suisse', 'Poste Suisse'),  # Switzerland
        ('postnord', 'PostNord'),  # Sweden/Norway
        ('bring', 'Bring'),  # Norway
        ('itella', 'Itella'),  # Finland
        ('cainiao', 'Cainiao'),  # China
        ('sf_express', 'SF Express'),  # China
        ('yunda', 'Yunda Express'),  # China
        ('zto', 'ZTO Express'),  # China
        ('sto', 'STO Express'),  # China
        ('yto', 'YTO Express'),  # China
        ('ems', 'EMS'),  # Global
        ('dhl_ecommerce', 'DHL eCommerce'),  # Global
        ('ups_mail_innovations', 'UPS Mail Innovations'),  # Global
        ('fedex_smartpost', 'FedEx SmartPost'),  # Global
        ('ontrac', 'OnTrac'),  # US
        ('lasership', 'LaserShip'),  # US
        ('amazon_logistics', 'Amazon Logistics'),  # Global
        ('aliexpress_logistics', 'AliExpress Logistics'),  # Global
        ('ebay_shipping', 'eBay Shipping'),  # Global
        ('wish_shipping', 'Wish Shipping'),  # Global
        ('dhgate_shipping', 'DHgate Shipping'),  # Global
        ('alibaba_logistics', 'Alibaba Logistics'),  # Global
        ('jd_logistics', 'JD Logistics'),  # China
        ('rakuten_logistics', 'Rakuten Logistics'),  # Japan
        ('lazada_logistics', 'Lazada Logistics'),  # Southeast Asia
        ('shopee_logistics', 'Shopee Logistics'),  # Southeast Asia
        ('tokopedia_logistics', 'Tokopedia Logistics'),  # Indonesia
        ('bukalapak_logistics', 'Bukalapak Logistics'),  # Indonesia
        ('blibli_logistics', 'Blibli Logistics'),  # Indonesia
        ('gojek_logistics', 'Gojek Logistics'),  # Indonesia
        ('grab_logistics', 'Grab Logistics'),  # Southeast Asia
        ('lalamove', 'Lalamove'),  # Asia
        ('ninjavan', 'NinjaVan'),  # Southeast Asia
        ('jne', 'JNE'),  # Indonesia
        ('tiki', 'TIKI'),  # Indonesia
        ('pos_indonesia', 'POS Indonesia'),  # Indonesia
        ('thailand_post', 'Thailand Post'),  # Thailand
        ('kerry_logistics', 'Kerry Logistics'),  # Thailand/Hong Kong
        ('dhl_supply_chain', 'DHL Supply Chain'),  # Global
        ('ups_supply_chain', 'UPS Supply Chain'),  # Global
        ('fedex_supply_chain', 'FedEx Supply Chain'),  # Global
        ('xpo_logistics', 'XPO Logistics'),  # Global
        ('c.h.robinson', 'C.H. Robinson'),  # Global
        ('kuehne_nagel', 'Kuehne + Nagel'),  # Global
        ('dbschenker', 'DB Schenker'),  # Global
        ('expeditors', 'Expeditors'),  # Global
        ('agility_logistics', 'Agility Logistics'),  # Global
        ('panalpina', 'Panalpina'),  # Global
        ('toll_group', 'Toll Group'),  # Australia/Global
        ('aramex_express', 'Aramex Express'),  # Global
        ('blue_dart', 'Blue Dart'),  # India
        ('delhivery', 'Delhivery'),  # India
        ('ecom_express', 'Ecom Express'),  # India
        ('first_flight', 'First Flight'),  # India
        ('gati', 'Gati'),  # India
        ('professional_couriers', 'Professional Couriers'),  # India
        ('shadowfax', 'Shadowfax'),  # India
        ('xpressbees', 'Xpressbees'),  # India
        ('dtdc', 'DTDC'),  # India
        ('omni_express', 'Omni Express'),  # Philippines
        ('jrs_express', 'JRS Express'),  # Philippines
        ('lbc_express', 'LBC Express'),  # Philippines
        ('2go_express', '2GO Express'),  # Philippines
        ('air21', 'AIR21'),  # Philippines
        ('dhl_active_tracing', 'DHL Active Tracing'),  # Global
        ('ups_returns', 'UPS Returns'),  # Global
        ('fedex_ground', 'FedEx Ground'),  # US/Canada
        ('ups_ground', 'UPS Ground'),  # US/Canada
        ('dhl_ground', 'DHL Ground'),  # US/Canada
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name='الطلب')
    provider = models.CharField(max_length=50, choices=SHIPPING_PROVIDER_CHOICES, verbose_name='مزود الشحن')
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
        unique_together = ('product', 'external_id', 'system_name')
    
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
        # Add more global event types
        ('wishlist_add', 'إضافة لقائمة الرغبات'),
        ('wishlist_remove', 'إزالة من قائمة الرغبات'),
        ('product_compare', 'مقارنة المنتجات'),
        ('review_add', 'إضافة تقييم'),
        ('review_helpful', 'تقييم مفيد'),
        ('share_product', 'مشاركة المنتج'),
        ('coupon_apply', 'تطبيق كوبون'),
        ('coupon_remove', 'إزالة كوبون'),
        ('loyalty_earn', 'كسب نقاط ولاء'),
        ('loyalty_redeem', 'استبدال نقاط ولاء'),
        ('newsletter_subscribe', 'الاشتراك في النشرة البريدية'),
        ('newsletter_unsubscribe', 'إلغاء الاشتراك في النشرة البريدية'),
        ('contact_form_submit', 'إرسال نموذج الاتصال'),
        ('live_chat_start', 'بدء الدردشة المباشرة'),
        ('live_chat_end', 'إنهاء الدردشة المباشرة'),
        ('support_ticket_create', 'إنشاء تذكرة دعم'),
        ('support_ticket_resolve', 'حل تذكرة دعم'),
        ('faq_view', 'عرض الأسئلة الشائعة'),
        ('blog_view', 'عرض المدونة'),
        ('article_view', 'عرض المقال'),
        ('category_view', 'عرض الفئة'),
        ('brand_view', 'عرض العلامة التجارية'),
        ('filter_apply', 'تطبيق الفلتر'),
        ('sort_change', 'تغيير الترتيب'),
        ('pagination_click', 'النقر على ترقيم الصفحات'),
        ('banner_click', 'النقر على البانر'),
        ('promotion_click', 'النقر على العرض الترويجي'),
        ('affiliate_click', 'النقر على الرابط التابع'),
        ('return_initiate', 'بدء الإرجاع'),
        ('return_complete', 'إكمال الإرجاع'),
        ('exchange_initiate', 'بدء الاستبدال'),
        ('exchange_complete', 'إكمال الاستبدال'),
        ('gift_card_purchase', 'شراء بطاقة هدية'),
        ('gift_card_redeem', 'استبدال بطاقة هدية'),
        ('subscription_start', 'بدء الاشتراك'),
        ('subscription_renew', 'تجديد الاشتراك'),
        ('subscription_cancel', 'إلغاء الاشتراك'),
        ('download_start', 'بدء التنزيل'),
        ('download_complete', 'إكمال التنزيل'),
        ('video_play', 'تشغيل الفيديو'),
        ('video_complete', 'إكمال الفيديو'),
        ('pdf_view', 'عرض PDF'),
        ('pdf_download', 'تنزيل PDF'),
        ('print_page', 'طباعة الصفحة'),
        ('email_share', 'مشاركة عبر البريد الإلكتروني'),
        ('sms_share', 'مشاركة عبر الرسائل القصيرة'),
        ('copy_link', 'نسخ الرابط'),
        ('qr_scan', 'مسح رمز QR'),
        ('voice_search', 'البحث الصوتي'),
        ('image_search', 'البحث بالصورة'),
        ('barcode_scan', 'مسح الباركود'),
        ('nfc_tap', 'النقر عبر NFC'),
        ('beacon_enter', 'دخول نطاق Beacon'),
        ('beacon_exit', 'خروج من نطاق Beacon'),
        ('geofence_enter', 'دخول نطاق جغرافي'),
        ('geofence_exit', 'خروج من نطاق جغرافي'),
        ('push_notification_receive', 'استلام إشعار فوري'),
        ('push_notification_click', 'النقر على إشعار فوري'),
        ('in_app_message_receive', 'استلام رسالة داخل التطبيق'),
        ('in_app_message_click', 'النقر على رسالة داخل التطبيق'),
        ('survey_start', 'بدء الاستبيان'),
        ('survey_complete', 'إكمال الاستبيان'),
        ('quiz_start', 'بدء الاختبار'),
        ('quiz_complete', 'إكمال الاختبار'),
        ('game_start', 'بدء اللعبة'),
        ('game_complete', 'إكمال اللعبة'),
        ('achievement_unlock', 'فتح الإنجاز'),
        ('level_up', 'الارتقاء بالمستوى'),
        ('virtual_currency_earn', 'كسب عملة افتراضية'),
        ('virtual_currency_spend', 'إنفاق عملة افتراضية'),
        ('social_login', 'تسجيل الدخول عبر وسائل التواصل'),
        ('social_share', 'مشاركة عبر وسائل التواصل'),
        ('social_invite', 'دعوة عبر وسائل التواصل'),
        ('social_follow', 'متابعة عبر وسائل التواصل'),
        ('social_unfollow', 'إلغاء المتابعة عبر وسائل التواصل'),
        ('social_mention', 'الإشارة عبر وسائل التواصل'),
        ('social_hashtag_click', 'النقر على الهاشتاغ'),
        ('social_dm_send', 'إرسال رسالة مباشرة'),
        ('social_dm_receive', 'استلام رسالة مباشرة'),
        ('social_story_view', 'عرض القصة'),
        ('social_story_share', 'مشاركة القصة'),
        ('social_live_view', 'عرض البث المباشر'),
        ('social_live_comment', 'تعليق على البث المباشر'),
        ('social_live_share', 'مشاركة البث المباشر'),
        ('social_poll_vote', 'التصويت في الاستطلاع'),
        ('social_poll_create', 'إنشاء استطلاع'),
        ('social_event_create', 'إنشاء حدث'),
        ('social_event_join', 'الانضمام إلى الحدث'),
        ('social_event_leave', 'مغادرة الحدث'),
        ('social_group_join', 'الانضمام إلى المجموعة'),
        ('social_group_leave', 'مغادرة المجموعة'),
        ('social_page_like', 'الإعجاب بالصفحة'),
        ('social_page_unlike', 'إلغاء الإعجاب بالصفحة'),
        ('social_checkin', 'تسجيل الدخول إلى الموقع'),
        ('social_location_tag', 'وضع علامة الموقع'),
        ('social_photo_upload', 'رفع صورة'),
        ('social_video_upload', 'رفع فيديو'),
        ('social_document_upload', 'رفع مستند'),
        ('social_audio_upload', 'رفع صوت'),
        ('social_file_download', 'تنزيل ملف'),
        ('social_file_share', 'مشاركة ملف'),
        ('social_calendar_add', 'إضافة إلى التقويم'),
        ('social_reminder_set', 'تعيين تذكير'),
        ('social_alarm_set', 'تعيين منبه'),
        ('social_timer_start', 'بدء المؤقت'),
        ('social_timer_stop', 'إيقاف المؤقت'),
        ('social_stopwatch_start', 'بدء ساعة التوقيت'),
        ('social_stopwatch_stop', 'إيقاف ساعة التوقيت'),
        ('social_countdown_start', 'بدء العد التنازلي'),
        ('social_countdown_stop', 'إيقاف العد التنازلي'),
        ('social_weather_check', 'التحقق من الطقس'),
        ('social_news_read', 'قراءة الأخبار'),
        ('social_bookmark_add', 'إضافة إشارة مرجعية'),
        ('social_bookmark_remove', 'إزالة إشارة مرجعية'),
        ('social_note_create', 'إنشاء ملاحظة'),
        ('social_note_edit', 'تحرير ملاحظة'),
        ('social_note_delete', 'حذف ملاحظة'),
        ('social_list_create', 'إنشاء قائمة'),
        ('social_list_edit', 'تحرير قائمة'),
        ('social_list_delete', 'حذف قائمة'),
        ('social_task_add', 'إضافة مهمة'),
        ('social_task_complete', 'إكمال مهمة'),
        ('social_task_delete', 'حذف مهمة'),
        ('social_reminder_create', 'إنشاء تذكير'),
        ('social_reminder_edit', 'تحرير تذكير'),
        ('social_reminder_delete', 'حذف تذكير'),
        ('social_alarm_create', 'إنشاء منبه'),
        ('social_alarm_edit', 'تحرير منبه'),
        ('social_alarm_delete', 'حذف منبه'),
        ('social_calendar_event_add', 'إضافة حدث إلى التقويم'),
        ('social_calendar_event_edit', 'تحرير حدث في التقويم'),
        ('social_calendar_event_delete', 'حذف حدث من التقويم'),
        ('social_contact_add', 'إضافة جهة اتصال'),
        ('social_contact_edit', 'تحرير جهة اتصال'),
        ('social_contact_delete', 'حذف جهة اتصال'),
        ('social_message_send', 'إرسال رسالة'),
        ('social_message_receive', 'استلام رسالة'),
        ('social_call_make', 'إجراء مكالمة'),
        ('social_call_receive', 'استلام مكالمة'),
        ('social_video_call_make', 'إجراء مكالمة فيديو'),
        ('social_video_call_receive', 'استلام مكالمة فيديو'),
        ('social_conference_call_start', 'بدء مكالمة جماعية'),
        ('social_conference_call_join', 'الانضمام إلى مكالمة جماعية'),
        ('social_conference_call_leave', 'مغادرة مكالمة جماعية'),
        ('social_conference_call_end', 'إنهاء مكالمة جماعية'),
        ('social_screen_share_start', 'بدء مشاركة الشاشة'),
        ('social_screen_share_stop', 'إيقاف مشاركة الشاشة'),
        ('social_remote_desktop_start', 'بدء سطح المكتب البعيد'),
        ('social_remote_desktop_stop', 'إيقاف سطح المكتب البعيد'),
        ('social_file_transfer_start', 'بدء نقل الملف'),
        ('social_file_transfer_complete', 'إكمال نقل الملف'),
        ('social_file_transfer_cancel', 'إلغاء نقل الملف'),
        ('social_print_start', 'بدء الطباعة'),
        ('social_print_complete', 'إكمال الطباعة'),
        ('social_print_cancel', 'إلغاء الطباعة'),
        ('social_scan_start', 'بدء المسح'),
        ('social_scan_complete', 'إكمال المسح'),
        ('social_scan_cancel', 'إلغاء المسح'),
        ('social_backup_start', 'بدء النسخ الاحتياطي'),
        ('social_backup_complete', 'إكمال النسخ الاحتياطي'),
        ('social_backup_cancel', 'إلغاء النسخ الاحتياطي'),
        ('social_restore_start', 'بدء الاستعادة'),
        ('social_restore_complete', 'إكمال الاستعادة'),
        ('social_restore_cancel', 'إلغاء الاستعادة'),
        ('social_sync_start', 'بدء المزامنة'),
        ('social_sync_complete', 'إكمال المزامنة'),
        ('social_sync_cancel', 'إلغاء المزامنة'),
        ('social_update_check', 'التحقق من التحديث'),
        ('social_update_download', 'تنزيل التحديث'),
        ('social_update_install', 'تثبيت التحديث'),
        ('social_update_complete', 'إكمال التحديث'),
        ('social_update_cancel', 'إلغاء التحديث'),
        ('social_install_start', 'بدء التثبيت'),
        ('social_install_complete', 'إكمال التثبيت'),
        ('social_install_cancel', 'إلغاء التثبيت'),
        ('social_uninstall_start', 'بدء إلغاء التثبيت'),
        ('social_uninstall_complete', 'إكمال إلغاء التثبيت'),
        ('social_uninstall_cancel', 'إلغاء إلغاء التثبيت'),
        ('social_repair_start', 'بدء الإصلاح'),
        ('social_repair_complete', 'إكمال الإصلاح'),
        ('social_repair_cancel', 'إلغاء الإصلاح'),
        ('social_optimize_start', 'بدء التحسين'),
        ('social_optimize_complete', 'إكمال التحسين'),
        ('social_optimize_cancel', 'إلغاء التحسين'),
        ('social_compress_start', 'بدء الضغط'),
        ('social_compress_complete', 'إكمال الضغط'),
        ('social_compress_cancel', 'إلغاء الضغط'),
        ('social_extract_start', 'بدء الاستخراج'),
        ('social_extract_complete', 'إكمال الاستخراج'),
        ('social_extract_cancel', 'إلغاء الاستخراج'),
        ('social_convert_start', 'بدء التحويل'),
        ('social_convert_complete', 'إكمال التحويل'),
        ('social_convert_cancel', 'إلغاء التحويل'),
        ('social_encrypt_start', 'بدء التشفير'),
        ('social_encrypt_complete', 'إكمال التشفير'),
        ('social_encrypt_cancel', 'إلغاء التشفير'),
        ('social_decrypt_start', 'بدء فك التشفير'),
        ('social_decrypt_complete', 'إكمال فك التشفير'),
        ('social_decrypt_cancel', 'إلغاء فك التشفير'),
        ('social_sign_start', 'بدء التوقيع'),
        ('social_sign_complete', 'إكمال التوقيع'),
        ('social_sign_cancel', 'إلغاء التوقيع'),
        ('social_verify_start', 'بدء التحقق'),
        ('social_verify_complete', 'إكمال التحقق'),
        ('social_verify_cancel', 'إلغاء التحقق'),
        ('social_auth_start', 'بدء المصادقة'),
        ('social_auth_complete', 'إكمال المصادقة'),
        ('social_auth_cancel', 'إلغاء المصادقة'),
        ('social_login_start', 'بدء تسجيل الدخول'),
        ('social_login_complete', 'إكمال تسجيل الدخول'),
        ('social_login_cancel', 'إلغاء تسجيل الدخول'),
        ('social_logout_start', 'بدء تسجيل الخروج'),
        ('social_logout_complete', 'إكمال تسجيل الخروج'),
        ('social_logout_cancel', 'إلغاء تسجيل الخروج'),
        ('social_register_start', 'بدء التسجيل'),
        ('social_register_complete', 'إكمال التسجيل'),
        ('social_register_cancel', 'إلغاء التسجيل'),
        ('social_password_reset_start', 'بدء إعادة تعيين كلمة المرور'),
        ('social_password_reset_complete', 'إكمال إعادة تعيين كلمة المرور'),
        ('social_password_reset_cancel', 'إلغاء إعادة تعيين كلمة المرور'),
        ('social_account_delete_start', 'بدء حذف الحساب'),
        ('social_account_delete_complete', 'إكمال حذف الحساب'),
        ('social_account_delete_cancel', 'إلغاء حذف الحساب'),
        ('social_account_suspend_start', 'بدء تعليق الحساب'),
        ('social_account_suspend_complete', 'إكمال تعليق الحساب'),
        ('social_account_suspend_cancel', 'إلغاء تعليق الحساب'),
        ('social_account_reactivate_start', 'بدء إعادة تفعيل الحساب'),
        ('social_account_reactivate_complete', 'إكمال إعادة تفعيل الحساب'),
        ('social_account_reactivate_cancel', 'إلغاء إعادة تفعيل الحساب'),
        ('social_account_upgrade_start', 'بدء ترقية الحساب'),
        ('social_account_upgrade_complete', 'إكمال ترقية الحساب'),
        ('social_account_upgrade_cancel', 'إلغاء ترقية الحساب'),
        ('social_account_downgrade_start', 'بدء خفض الحساب'),
        ('social_account_downgrade_complete', 'إكمال خفض الحساب'),
        ('social_account_downgrade_cancel', 'إلغاء خفض الحساب'),
        ('social_subscription_upgrade_start', 'بدء ترقية الاشتراك'),
        ('social_subscription_upgrade_complete', 'إكمال ترقية الاشتراك'),
        ('social_subscription_upgrade_cancel', 'إلغاء ترقية الاشتراك'),
        ('social_subscription_downgrade_start', 'بدء خفض الاشتراك'),
        ('social_subscription_downgrade_complete', 'إكمال خفض الاشتراك'),
        ('social_subscription_downgrade_cancel', 'إلغاء خفض الاشتراك'),
        ('social_payment_start', 'بدء الدفع'),
        ('social_payment_complete', 'إكمال الدفع'),
        ('social_payment_cancel', 'إلغاء الدفع'),
        ('social_refund_start', 'بدء الاسترداد'),
        ('social_refund_complete', 'إكمال الاسترداد'),
        ('social_refund_cancel', 'إلغاء الاسترداد'),
        ('social_chargeback_start', 'بدء الخصم الراجع'),
        ('social_chargeback_complete', 'إكمال الخصم الراجع'),
        ('social_chargeback_cancel', 'إلغاء الخصم الراجع'),
        ('social_dispute_start', 'بدء النزاع'),
        ('social_dispute_complete', 'إكمال النزاع'),
        ('social_dispute_cancel', 'إلغاء النزاع'),
        ('social_resolution_start', 'بدء الحل'),
        ('social_resolution_complete', 'إكمال الحل'),
        ('social_resolution_cancel', 'إلغاء الحل'),
        ('social_feedback_submit', 'إرسال التغذية الراجعة'),
        ('social_review_submit', 'إرسال المراجعة'),
        ('social_rating_submit', 'إرسال التقييم'),
        ('social_comment_submit', 'إرسال التعليق'),
        ('social_reply_submit', 'إرسال الرد'),
        ('social_like_submit', 'إرسال الإعجاب'),
        ('social_dislike_submit', 'إرسال عدم الإعجاب'),
        ('social_share_submit', 'إرسال المشاركة'),
        ('social_report_submit', 'إرسال التبليغ'),
        ('social_block_submit', 'إرسال الحظر'),
        ('social_unblock_submit', 'إرسال إلغاء الحظر'),
        ('social_follow_submit', 'إرسال المتابعة'),
        ('social_unfollow_submit', 'إرسال إلغاء المتابعة'),
        ('social_subscribe_submit', 'إرسال الاشتراك'),
        ('social_unsubscribe_submit', 'إرسال إلغاء الاشتراك'),
        ('social_invite_submit', 'إرسال الدعوة'),
        ('social_accept_submit', 'إرسال القبول'),
        ('social_decline_submit', 'إرسال الرفض'),
        ('social_cancel_submit', 'إرسال الإلغاء'),
        ('social_confirm_submit', 'إرسال التأكيد'),
        ('social_approve_submit', 'إرسال الموافقة'),
        ('social_reject_submit', 'إرسال الرفض'),
        ('social_pending_submit', 'إرسال الانتظار'),
        ('social_complete_submit', 'إرسال الإكمال'),
        ('social_fail_submit', 'إرسال الفشل'),
        ('social_success_submit', 'إرسال النجاح'),
        ('social_error_submit', 'إرسال الخطأ'),
        ('social_warning_submit', 'إرسال التحذير'),
        ('social_info_submit', 'إرسال المعلومات'),
        ('social_debug_submit', 'إرسال التصحيح'),
        ('social_trace_submit', 'إرسال التتبع'),
        ('social_log_submit', 'إرسال السجل'),
        ('social_audit_submit', 'إرسال التدقيق'),
        ('social_compliance_submit', 'إرسال الامتثال'),
        ('social_security_submit', 'إرسال الأمان'),
        ('social_privacy_submit', 'إرسال الخصوصية'),
        ('social_terms_submit', 'إرسال الشروط'),
        ('social_policy_submit', 'إرسال السياسة'),
        ('social_agreement_submit', 'إرسال الاتفاق'),
        ('social_contract_submit', 'إرسال العقد'),
        ('social_license_submit', 'إرسال الترخيص'),
        ('social_permission_submit', 'إرسال الإذن'),
        ('social_authorization_submit', 'إرسال التفويض'),
        ('social_authentication_submit', 'إرسال المصادقة'),
        ('social_identification_submit', 'إرسال الهوية'),
        ('social_verification_submit', 'إرسال التحقق'),
        ('social_certification_submit', 'إرسال الشهادة'),
        ('social_accreditation_submit', 'إرسال الاعتماد'),
        ('social_qualification_submit', 'إرسال المؤهل'),
        ('social_education_submit', 'إرسال التعليم'),
        ('social_training_submit', 'إرسال التدريب'),
        ('social_skill_submit', 'إرسال المهارة'),
        ('social_expertise_submit', 'إرسال الخبرة'),
        ('social_experience_submit', 'إرسال التجربة'),
        ('social_achievement_submit', 'إرسال الإنجاز'),
        ('social_recognition_submit', 'إرسال الاعتراف'),
        ('social_award_submit', 'إرسال الجائزة'),
        ('social_honor_submit', 'إرسال الشرف'),
        ('social_prestige_submit', 'إرسال الاحترام'),
        ('social_reputation_submit', 'إرسال السمعة'),
        ('social_trust_submit', 'إرسال الثقة'),
        ('social_credibility_submit', 'إرسال المصداقية'),
        ('social_reliability_submit', 'إرسال الموثوقية'),
        ('social_consistency_submit', 'إرسال الاتساق'),
        ('social_accuracy_submit', 'إرسال الدقة'),
        ('social_precision_submit', 'إرسال التحديد'),
        ('social_exactness_submit', 'إرسال الدقة التامة'),
        ('social_correctness_submit', 'إرسال الصحة'),
        ('social_validity_submit', 'إرسال الصلاحية'),
        ('social_legitimacy_submit', 'إرسال الشرعية'),
        ('social_authenticity_submit', 'إرسال الأصالة'),
        ('social_genuineness_submit', 'إرسال الأصالة'),
        ('social_originality_submit', 'إرسال الأصالة'),
        ('social_uniqueness_submit', 'إرسال التفرد'),
        ('social_exclusivity_submit', 'إرسال الحصرية'),
        ('social_rarity_submit', 'إرسال الندرة'),
        ('social_scarcity_submit', 'إرسال الندرة'),
        ('social_availability_submit', 'إرسال التوفر'),
        ('social_accessibility_submit', 'إرسال إمكانية الوصول'),
        ('social_usability_submit', 'إرسال إمكانية الاستخدام'),
        ('social_functionality_submit', 'إرسال الوظائف'),
        ('social_performance_submit', 'إرسال الأداء'),
        ('social_efficiency_submit', 'إرسال الكفاءة'),
        ('social_effectiveness_submit', 'إرسال الفعالية'),
        ('social_productivity_submit', 'إرسال الإنتاجية'),
        ('social_quality_submit', 'إرسال الجودة'),
        ('social_excellence_submit', 'إرسال التميز'),
        ('social_superiority_submit', 'إرسال التفوق'),
        ('social_advantage_submit', 'إرسال الميزة'),
        ('social_benefit_submit', 'إرسال الفائدة'),
        ('social_value_submit', 'إرسال القيمة'),
        ('social_worth_submit', 'إرسال القيمة'),
        ('social_importance_submit', 'إرسال الأهمية'),
        ('social_significance_submit', 'إرسال الأهمية'),
        ('social_relevance_submit', 'إرسال الصلة'),
        ('social_pertinence_submit', 'إرسال الصلة'),
        ('social_applicability_submit', 'إرسال القابلية للتطبيق'),
        ('social_utility_submit', 'إرسال الفائدة'),
        ('social_usefulness_submit', 'إرسال الفائدة'),
        ('social_practicality_submit', 'إرسال العملية'),
        ('social_convenience_submit', 'إرسال الراحة'),
        ('social_comfort_submit', 'إرسال الراحة'),
        ('social_satisfaction_submit', 'إرسال الرضا'),
        ('social_pleasure_submit', 'إرسال المتعة'),
        ('social_enjoyment_submit', 'إرسال الاستمتاع'),
        ('social_entertainment_submit', 'إرسال الترفيه'),
        ('social_recreation_submit', 'إرسال الترفيه'),
        ('social_leisure_submit', 'إرسال وقت الفراغ'),
        ('social_relaxation_submit', 'إرسال الاسترخاء'),
        ('social_stress_relief_submit', 'إرسال تخفيف التوتر'),
        ('social_wellness_submit', 'إرسال الرفاهية'),
        ('social_health_submit', 'إرسال الصحة'),
        ('social_fitness_submit', 'إرسال اللياقة'),
        ('social_nutrition_submit', 'إرسال التغذية'),
        ('social_diet_submit', 'إرسال النظام الغذائي'),
        ('social_exercise_submit', 'إرسال التمارين'),
        ('social_workout_submit', 'إرسال التمارين'),
        ('social_training_submit', 'إرسال التدريب'),
        ('social_coaching_submit', 'إرسال التدريب'),
        ('social_mentoring_submit', 'إرسال الإرشاد'),
        ('social_guidance_submit', 'إرسال التوجيه'),
        ('social_advice_submit', 'إرسال النصيحة'),
        ('social_counsel_submit', 'إرسال الاستشارة'),
        ('social_consultation_submit', 'إرسال الاستشارة'),
        ('social_therapy_submit', 'إرسال العلاج'),
        ('social_healing_submit', 'إرسال الشفاء'),
        ('social_recovery_submit', 'إرسال التعافي'),
        ('social_rehabilitation_submit', 'إرسال إعادة التأهيل'),
        ('social_restoration_submit', 'إرسال الاستعادة'),
        ('social_renewal_submit', 'إرسال التجديد'),
        ('social_revival_submit', 'إرسال الإحياء'),
        ('social_resurrection_submit', 'إرسال البعث'),
        ('social_rebirth_submit', 'إرسال الولادة الجديدة'),
        ('social_transformation_submit', 'إرسال التحول'),
        ('social_metamorphosis_submit', 'إرسال التحول'),
        ('social_evolution_submit', 'إرسال التطور'),
        ('social_progress_submit', 'إرسال التقدم'),
        ('social_advancement_submit', 'إرسال التقدم'),
        ('social_improvement_submit', 'إرسال التحسين'),
        ('social_enhancement_submit', 'إرسال التحسين'),
        ('social_optimization_submit', 'إرسال التحسين'),
        ('social_refinement_submit', 'إرسال التحسين'),
        ('social_polishing_submit', 'إرسال التلميع'),
        ('social_perfection_submit', 'إرسال الكمال'),
        ('social_excellence_submit', 'إرسال التميز'),
        ('social_supremacy_submit', 'إرسال التفوق'),
        ('social_dominance_submit', 'إرسال الهيمنة'),
        ('social_leadership_submit', 'إرسال القيادة'),
        ('social_management_submit', 'إرسال الإدارة'),
        ('social_governance_submit', 'إرسال الحوكمة'),
        ('social_control_submit', 'إرسال السيطرة'),
        ('social_direction_submit', 'إرسال التوجيه'),
        ('social_guidance_submit', 'إرسال التوجيه'),
        ('social_navigation_submit', 'إرسال التنقل'),
        ('social_steering_submit', 'إرسال التوجيه'),
        ('social_piloting_submit', 'إرسال القيادة'),
        ('social_driving_submit', 'إرسال القيادة'),
        ('social_motivation_submit', 'إرسال الحافز'),
        ('social_inspiration_submit', 'إرسال الإلهام'),
        ('social_encouragement_submit', 'إرسال التشجيع'),
        ('social_support_submit', 'إرسال الدعم'),
        ('social_assistance_submit', 'إرسال المساعدة'),
        ('social_help_submit', 'إرسال المساعدة'),
        ('social_aid_submit', 'إرسال المساعدة'),
        ('social_relief_submit', 'إرسال الإغاثة'),
        ('social_rescue_submit', 'إرسال الإنقاذ'),
        ('social_salvation_submit', 'إرسال الخلاص'),
        ('social_redemption_submit', 'إرسال الفداء'),
        ('social_liberation_submit', 'إرسال التحرير'),
        ('social_emancipation_submit', 'إرسال التحرير'),
        ('social_freedom_submit', 'إرسال الحرية'),
        ('social_independence_submit', 'إرسال الاستقلال'),
        ('social_autonomy_submit', 'إرسال الاستقلال'),
        ('social_self_reliance_submit', 'إرسال الاعتماد على النفس'),
        ('social_self_sufficiency_submit', 'إرسال الكفاية الذاتية'),
        ('social_sustainability_submit', 'إرسال الاستدامة'),
        ('social_ecology_submit', 'إرسال البيئة'),
        ('social_environment_submit', 'إرسال البيئة'),
        ('social_nature_submit', 'إرسال الطبيعة'),
        ('social_wildlife_submit', 'إرسال الحياة البرية'),
        ('social_conservation_submit', 'إرسال الحفظ'),
        ('social_preservation_submit', 'إرسال الحفظ'),
        ('social_protection_submit', 'إرسال الحماية'),
        ('social_defense_submit', 'إرسال الدفاع'),
        ('social_security_submit', 'إرسال الأمن'),
        ('social_safety_submit', 'إرسال السلامة'),
        ('social_peace_submit', 'إرسال السلام'),
        ('social_harmony_submit', 'إرسال التناغم'),
        ('social_balance_submit', 'إرسال التوازن'),
        ('social_stability_submit', 'إرسال الاستقرار'),
        ('social_order_submit', 'إرسال النظام'),
        ('social_discipline_submit', 'إرسال الانضباط'),
        ('social_structure_submit', 'إرسال الهيكل'),
        ('social_organization_submit', 'إرسال التنظيم'),
        ('social_system_submit', 'إرسال النظام'),
        ('social_process_submit', 'إرسال العملية'),
        ('social_procedure_submit', 'إرسال الإجراء'),
        ('social_protocol_submit', 'إرسال البروتوكول'),
        ('social_standard_submit', 'إرسال المعيار'),
        ('social_norm_submit', 'إرسال القاعدة'),
        ('social_rule_submit', 'إرسال القاعدة'),
        ('social_law_submit', 'إرسال القانون'),
        ('social_regulation_submit', 'إرسال التنظيم'),
        ('social_policy_submit', 'إرسال السياسة'),
        ('social_strategy_submit', 'إرسال الاستراتيجية'),
        ('social_plan_submit', 'إرسال الخطة'),
        ('social_project_submit', 'إرسال المشروع'),
        ('social_program_submit', 'إرسال البرنامج'),
        ('social_initiative_submit', 'إرسال المبادرة'),
        ('social_campaign_submit', 'إرسال الحملة'),
        ('social_movement_submit', 'إرسال الحركة'),
        ('social_revolution_submit', 'إرسال الثورة'),
        ('social_reform_submit', 'إرسال الإصلاح'),
        ('social_change_submit', 'إرسال التغيير'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='المستخدم')
    session_key = models.CharField(max_length=40, null=True, blank=True, verbose_name='مفتاح الجلسة')
    event_type = models.CharField(max_length=255, choices=EVENT_TYPE_CHOICES, verbose_name='نوع الحدث')
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
    event_type = models.CharField(max_length=255, choices=EVENT_TYPES, verbose_name='نوع الحدث')
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
    views = models.PositiveIntegerField(default=0, verbose_name='المشاهدات')  # type: ignore
    
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
    is_read = models.BooleanField(default=False, verbose_name='مقروء')  # type: ignore
    
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
    is_internal_note = models.BooleanField(default=False, verbose_name='ملاحظة داخلية')  # type: ignore
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
    order = models.PositiveIntegerField(default=0, verbose_name='الترتيب')  # type: ignore
    is_active = models.BooleanField(default=True, verbose_name='مفعل')  # type: ignore
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
    order = models.PositiveIntegerField(default=0, verbose_name='الترتيب')  # type: ignore
    is_active = models.BooleanField(default=True, verbose_name='مفعل')  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    views = models.PositiveIntegerField(default=0, verbose_name='المشاهدات')  # type: ignore
    
    class Meta:
        verbose_name = 'سؤال شائع'
        verbose_name_plural = 'الأسئلة الشائعة'
        ordering = ['order']
    
    def __str__(self) -> str:
        return str(self.question)

# Enhanced Review Model
class WithdrawalRequest(models.Model):
    """Model for seller payout/withdrawal requests"""
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('approved', 'موافق عليه'),
        ('processing', 'قيد المعالجة'),
        ('completed', 'مكتمل'),
        ('rejected', 'مرفوض'),
    ]
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='البائع', related_name='withdrawal_requests')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='المبلغ')
    currency = models.CharField(max_length=3, choices=Product.CURRENCY_CHOICES, default='USD', verbose_name='العملة')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    payment_method = models.CharField(max_length=50, verbose_name='طريقة الدفع')
    bank_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='اسم البنك')
    bank_account_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='رقم الحساب البنكي')
    iban = models.CharField(max_length=50, blank=True, null=True, verbose_name='IBAN')
    paypal_email = models.EmailField(blank=True, null=True, verbose_name='بريد باي بال')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ المعالجة')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الإكمال')
    
    class Meta:
        verbose_name = 'طلب سحب'
        verbose_name_plural = 'طلبات السحب'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        username = getattr(self.seller, 'username', 'Unknown Seller')
        return f"طلب سحب #{self.pk} - {username} - {self.amount} {self.currency}"
    
    def get_status_display_arabic(self) -> str:
        """Get Arabic status display"""
        status_dict = dict(self.STATUS_CHOICES)
        return status_dict.get(self.status, self.status)


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
    is_verified_purchase = models.BooleanField(default=False, verbose_name='شراء مؤكد')  # type: ignore
    is_featured = models.BooleanField(default=False, verbose_name='مميز')  # type: ignore
    helpful_count = models.PositiveIntegerField(default=0, verbose_name='عدد المساعدين')  # type: ignore
    not_helpful_count = models.PositiveIntegerField(default=0, verbose_name='عدد غير المساعدين')  # type: ignore
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
        total_votes = self.helpful_count + self.not_helpful_count  # type: ignore
        if total_votes == 0:
            return 0
        return int((self.helpful_count / total_votes) * 100)  # type: ignore
