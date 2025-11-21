import os
from pathlib import Path

# استيراد dj_database_url
import dj_database_url

# ===========================
# إعدادات المسارات العامة
# ===========================
BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================
# إعدادات الأمان
# ===========================
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-key')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ===========================
# التطبيقات المثبتة
# ===========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ضع هنا تطبيقاتك الخاصة، مثل:
    'store',
    # 'users',
    'channels',
]

# ===========================
# إعدادات Middleware
# ===========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Add this for internationalization
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ===========================
# إعداد URL و WSGI
# ===========================
# غيّر 'shopsite' إلى اسم مجلد مشروعك الرئيسي
ROOT_URLCONF = 'shopsite.urls'
WSGI_APPLICATION = 'shopsite.wsgi.application'
ASGI_APPLICATION = 'shopsite.asgi.application'

# ===========================
# إعداد قاعدة البيانات
# ===========================
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ===========================
# الملفات الثابتة (Static)
# ===========================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ===========================
# الملفات الإعلامية (Media)
# ===========================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===========================
# القوالب (Templates)
# ===========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # مجلد القوالب
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'store.context_processors.cart_processor',
                'store.context_processors.notifications_processor',
            ],
        },
    },
]

# ===========================
# اللغة والمنطقة الزمنية
# ===========================
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Aden'
USE_I18N = True
USE_TZ = True

# Add internationalization settings for global support
LANGUAGES = [
    ('ar', 'Arabic'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# ===========================
# ملفات الأمن
# ===========================
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ===========================
# Caching Configuration
# ===========================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# ===========================
# نهاية الملف
# ===========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'