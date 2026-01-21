import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.settings')
django.setup()

from chat.models import ChatRoom

def clean_chats():
    count = ChatRoom.objects.count()
    ChatRoom.objects.all().delete()
    print(f"Deleted {count} chat rooms.")

if __name__ == "__main__":
    clean_chats()
