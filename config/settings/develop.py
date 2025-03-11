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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'default_db'),
        'USER': os.getenv('DB_USER', 'default_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'default_password'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),  # Default to local MySQL
        'PORT': os.getenv('DB_PORT', '3306'),  # Default MySQL port
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

MEDIA_ROOT = str(BASE_DIR / 'media')
STATIC_ROOT = str(BASE_DIR / 'templates')

STATIC_URL = '/assets/'
MEDIA_URL = '/media/'