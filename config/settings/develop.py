import os
from .settings import *
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': os.environ.get('POSTGRES_PORT'),
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

MEDIA_ROOT = str(BASE_DIR / 'media')
STATIC_ROOT = str(BASE_DIR / 'templates')

STATIC_URL = '/assets/'
MEDIA_URL = '/media/'