import os
from dotenv import load_dotenv
from .settings import *
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Fix: Point to project root (settings -> config -> speedy-transfer)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables
print(f"BASE_DIR: {BASE_DIR}")
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Add Jet Dashboard and Jet to installed apps (must be before django.contrib.admin)
INSTALLED_APPS = [
    'jet.dashboard',
    'jet',
] + INSTALLED_APPS

DEBUG = True

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# Try to use MySQL if available, otherwise fall back to SQLite for development
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'speedy'),
            'USER': os.getenv('DB_USER', 'speedy_user'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'speedy_password'),
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            }
        },
        'reports': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'speedy'),
            'USER': os.getenv('DB_USER', 'speedy_user'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'speedy_password'),
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            }
        }
    }
    # Database routers
    DATABASE_ROUTERS = ['reports.router.ReportsRouter']
except ImportError:
    # Fallback to SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        },
        'reports': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    # Database routers
    DATABASE_ROUTERS = ['reports.router.ReportsRouter']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

MEDIA_ROOT = str(BASE_DIR / 'media')
#STATIC_ROOT = str(BASE_DIR / 'templates')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATIC_URL = '/assets/'
MEDIA_URL = '/media/'

# Simple in-memory caching for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

# WhiteNoise settings - in production use compressed manifest storage.
# During tests or local DEBUG runs we prefer the simple storage to avoid
# MissingManifest errors when static files haven't been collected.
import sys
if 'test' in ' '.join(sys.argv):
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    # STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Payment Configuration - Override with environment variables
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', '')
PAYPAL_SECRET = os.getenv('PAYPAL_SECRET', '')

# Twilio/WhatsApp configuration (use environment variables; do NOT commit secrets)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
# Twilio WhatsApp from number in format 'whatsapp:+1415...'
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')

# Email Configuration - Zoho Mail SMTP Settings
# Override with environment variables if needed
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.zoho.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '465'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'info@speedytransfers.mx')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'Aja.yyt5')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'info@speedytransfers.mx')

# Configure SSL/TLS based on port
if EMAIL_PORT == 465:
    EMAIL_USE_SSL = True
    EMAIL_USE_TLS = False
elif EMAIL_PORT == 587:
    EMAIL_USE_SSL = False
    EMAIL_USE_TLS = True
else:
    # Default to SSL for other ports
    EMAIL_USE_SSL = True
    EMAIL_USE_TLS = False

# Fix SSL certificate verification issues
EMAIL_SSL_CERTVERIFY = False

# For local development, use the custom SMTP backend (same as production)
# This ensures emails are actually sent during development
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'speedy_app.core.email_backend.CustomSMTPEmailBackend')