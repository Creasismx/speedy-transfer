
import os
import django
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
import sys
import platform

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.develop')
django.setup()

def test_email():
    print(f"Python version: {platform.python_version()}")
    print(f"Django version: {django.get_version()}")
    print("-" * 50)
    print("📧 Checking Email Configuration...")
    print(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Not Set')}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not Set')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not Set')}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not Set')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not Set')}")
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not Set')}")
    print("-" * 50)

    recipient = 'info@speedytransfers.mx' # Trying the one in views.py
    
    subject = "Test Email from Debug Script"
    text_content = "This is a test email to verify the outgoing email configuration."
    html_content = "<p>This is a <strong>test email</strong> to verify the outgoing email configuration.</p>"
    
    print(f"🚀 Attempting to send test email to {recipient}...")
    
    try:
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [recipient]
        )
        msg.attach_alternative(html_content, "text/html")
        result = msg.send(fail_silently=False)
        
        if result == 1:
            print("✅ Email sent successfully!")
        else:
            print(f"⚠️ Email send returned {result} (expected 1)")
            
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_email()
