DEBUG = False
ALLOWED_HOSTS = ['speedyvallarta.com', 'www.speedyvallarta.com']

from dotenv import load_dotenv
import os

load_dotenv(os.path.join(BASE_DIR, '.env'))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'speedy_db',
        'USER': 'speedy_user',
        'PASSWORD': '71Du$1WJ>bvv]iw',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")

# PayPal
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")

# Other settings
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-key")
DEBUG = os.getenv("DEBUG", "True") == "True"

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

