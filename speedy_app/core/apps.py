from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'speedy_app.core'
    
    def ready(self):
        # Import admin modules to ensure all models are registered
        # This must happen in ready() to ensure all apps are loaded first
        import chat.admin  # noqa
        # Import and apply the admin URL wrapper after all registrations are complete
        from speedy_app.core.admin import get_admin_urls
        from django.contrib import admin
        # Apply the URL wrapper now that all models should be registered
        admin.site.get_urls = get_admin_urls(admin.site.get_urls)