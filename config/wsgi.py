"""
WSGI config for SpeedyTransfers project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import sys
import collections
import collections.abc

# Monkey patch for Python 3.10+ compatibility
if not hasattr(collections, 'MutableSet'):
    collections.MutableSet = collections.abc.MutableSet

import pymysql
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Configure PyMySQL as MySQL DB connector
pymysql.install_as_MySQLdb()

# Load environment variables from .env file if it exists
from dotenv import load_dotenv
env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Apply runtime patches for Python 3.13 compatibility
try:
    from speedy_app.core.monkey_patches import apply_multipart_fix
    apply_multipart_fix()
except ImportError:
    pass

from django.core.wsgi import get_wsgi_application

# Ensure DJANGO_SETTINGS_MODULE is set
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'

# Initialize WSGI application
application = get_wsgi_application()

# Vercel handler
app = application
