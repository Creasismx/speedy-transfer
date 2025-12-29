import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.develop')
import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'admin'
new_password = 'admin123'

try:
    if User.objects.filter(username=username).exists():
        u = User.objects.get(username=username)
        u.set_password(new_password)
        u.save()
        print(f"Successfully reset password for '{username}' to '{new_password}'")
    else:
        User.objects.create_superuser(username=username, email='admin@example.com', password=new_password)
        print(f"Created new superuser '{username}' with password '{new_password}'")
except Exception as e:
    print(f"Error: {e}")
