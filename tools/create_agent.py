import os
import django
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.settings')
django.setup()

from django.contrib.auth.models import User
from chat.models import ChatAgent

def create_test_agent():
    username = 'agent_test'
    password = 'SpeedyAgent2026!'
    email = 'agent@speedytransfers.mx'

    try:
        # Create or get User
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.set_password(password)
            user.email = email
            user.save()
            print(f"Updated existing user '{username}' with new password.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            print(f"Created new user '{username}'.")

        # Create or update ChatAgent
        agent, created = ChatAgent.objects.get_or_create(user=user)
        agent.is_available = True
        agent.save()
        
        if created:
            print(f"Linked user '{username}' to ChatAgent profile.")
        else:
            print(f"User '{username}' already has a ChatAgent profile (ensured availability=True).")

        print("\nCredentials:")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Login URL: /chat/login")

    except Exception as e:
        print(f"Error creating agent: {e}")

if __name__ == "__main__":
    create_test_agent()
