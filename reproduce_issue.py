
import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.develop")
django.setup()

from speedy_app.core.models import Certificate

def run():
    print("Attempting to create Certificate with image...")
    
    # Create a small dummy image
    img_io = BytesIO()
    image = Image.new('RGB', (100, 100), color='red')
    image.save(img_io, format='JPEG')
    img_content = img_io.getvalue()
    
    uploaded_file = SimpleUploadedFile(
        name='test_image.jpg',
        content=img_content,
        content_type='image/jpeg'
    )
    
    try:
        cert = Certificate(
            title="Test Certificate",
            image=uploaded_file,
            certificate_type='certificate'
        )
        cert.save()
        print(f"Success! Created certificate with ID: {cert.id}")
        
    except Exception as e:
        print(f"FAILED to save certificate: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run()
