
import sys
import platform

print(f"Python Architecture: {platform.architecture()}")
print(f"Python Version: {sys.version}")

try:
    import cgi
    print("✅ 'cgi' module is available.")
    if hasattr(cgi, 'parse_header'):
        print("✅ 'cgi.parse_header' is available.")
    else:
        print("❌ 'cgi.parse_header' is MISSING.")
except ImportError:
    print("❌ 'cgi' module is MISSING (This invalidates Django 3.2).")

try:
    import django
    print(f"Django Version: {django.get_version()}")
except ImportError:
    print("❌ Django is not installed.")
