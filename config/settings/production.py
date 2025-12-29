import os
from pathlib import Path
from .settings import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Temporarily enable debug for troubleshooting
DEBUG = False

# Allow hosts (set via environment variable in production)
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# Increase max upload size to 50MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024

# Add logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Static files (CSS, JavaScript, Images)
# Use /assets/ to match local development settings
STATIC_URL = '/assets/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates')
STATICFILES_DIRS = [
    os.path.join(TEMPLATE_PATH, 'assets'),
]

# Use WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Ensure WhiteNoise can find files
WHITENOISE_ROOT = STATIC_ROOT

# Template configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
        },
    },
]

# Override INSTALLED_APPS to remove development-only apps
INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'speedy_app.core',
    'channels',
    'rest_framework',
    'corsheaders',
    'chat',
    'reports',
]

# Database - use external MySQL database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'speedy'),
        'USER': os.getenv('DB_USER', 'speedy_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', '71Du$1WJ>bvv]iw'),
        'HOST': os.getenv('DB_HOST', '45.82.72.136'),
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
        'PASSWORD': os.getenv('DB_PASSWORD', '71Du$1WJ>bvv]iw'),
        'HOST': os.getenv('DB_HOST', '45.82.72.136'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
    }
}

# Database routers
DATABASE_ROUTERS = ['reports.router.ReportsRouter']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True

# WebSocket settings
ASGI_APPLICATION = 'config.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# CORS settings - configure specific origins via environment if needed
CORS_ALLOWED_ORIGINS = []
CORS_ORIGIN_ALLOW_ALL = True # Allow all to avoid 400 errors during debug/prod transition