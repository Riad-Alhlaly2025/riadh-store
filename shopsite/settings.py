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
ALLOWED_HOSTS = ['*']  # لاحقًا يمكنك وضع نطاق موقعك مثل ['yourappname.onrender.com']

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
]

# ===========================
# إعدادات Middleware
# ===========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # لعرض ملفات static
    'django.contrib.sessions.middleware.SessionMiddleware',
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

# ===========================
# إعداد قاعدة البيانات
# ===========================
if 'DATABASE_URL' in os.environ:
    # استخدام قاعدة بيانات Heroku (PostgreSQL)
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ['DATABASE_URL'],
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # استخدام قاعدة بيانات SQLite محليًا
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / 'db.sqlite3'),
        }
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

# ===========================
# ملفات الأمن
# ===========================
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ===========================
# نهاية الملف
# ===========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'