import os
from dotenv import load_dotenv
from .settings import *
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
print(BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, '../.env'))

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
        }
    }
except ImportError:
    # Fallback to SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

MEDIA_ROOT = str(BASE_DIR / 'media')
#STATIC_ROOT = str(BASE_DIR / 'templates')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATIC_URL = '/assets/'
MEDIA_URL = '/media/'