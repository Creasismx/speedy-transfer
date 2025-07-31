# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django JET URLs MUST come BEFORE admin.site.urls
    # These lines were previously commented out. Uncomment them.
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    
    # Standard Django Admin URLs
    path('admin/', admin.site.urls),
    
    # Your core app URLs
    # Ensure the namespace matches app_name in speedy_app/core/urls.py (which is 'core')
    path('', include('speedy_app.core.urls', namespace='core')),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_URL) # Corrected MEDIA_URL here
