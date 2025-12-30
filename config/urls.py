# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),  # Django Jet URLs
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django Jet Dashboard URLs
    path('admin/', admin.site.urls),
	path('', include('speedy_app.core.urls', namespace='core')),
	# Reporting panel with separate login/dashboard
	path('reports/', include('reports.urls', namespace='reports')),
	# Chat system URLs
	path('chat/', include('chat.urls', namespace='chat')),
	# Serve a minimal inline SVG as a favicon so browsers don't hit a 404 for /favicon.ico
	path('favicon.ico', lambda request: HttpResponse(
		'<?xml version="1.0" encoding="utf-8"?>\n'
		'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">\n'
		'  <rect width="100%" height="100%" fill="#007bff"/>\n'
		'  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"\n'
		'        font-family="Arial, Helvetica, sans-serif" font-size="34" fill="#fff">S</text>\n'
		'</svg>', content_type='image/svg+xml')),
]

from django.views.static import serve
from django.urls import re_path

# Serve static and media files manually to ensure they work in all environments
# (including 'runserver' with DEBUG=False where they are normally disabled)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^assets/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

