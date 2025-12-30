import os
import logging
import collections
import collections.abc

# Monkey patch for Python 3.10+ compatibility
if not hasattr(collections, 'MutableSet'):
    collections.MutableSet = collections.abc.MutableSet

from django.core.asgi import get_asgi_application

# Configure logging
logger = logging.getLogger(__name__)

# Set Django settings module (use develop for local, production for deployment)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('DJANGO_SETTINGS_MODULE', 'config.settings.develop'))

# Get Django ASGI application first
django_asgi_app = get_asgi_application()

# Import Django and set it up
import django
django.setup()

# Import other dependencies after Django is set up
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Import websocket patterns last
from chat.routing import websocket_urlpatterns

# Create application
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})