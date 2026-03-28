
import os
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.settings')
django.setup()

from speedy_app.core.views import create_booking_record
from speedy_app.core.models import Car, CarType

def test_booking_creation():
    print("Testing create_booking_record...")
    
    # Ensure a car exists
    car = Car.objects.first()
    if not car:
        print("Creating test car...")
        ct = CarType.objects.first() or CarType.objects.create(code='TEST', name='Test')
        car = Car.objects.create(name='Test Car', car_type=ct, max=4)
        print(f"Test car created: {car}")

    order_data = {
        'total': '100.00',
        'currency': 'USD',
        'people': 2,
        'trip_type': 'oneway',
        'customer': {
            'email': 'test@example.com',
            'name': 'Test User',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '1234567890',
            'zip': '12345',
            'country': 'US'
        },
        'pickup': {
            'location_name': 'Airport',
            'datetime': '2025-12-25T10:00:00'
        },
        'dropoff': {
            'location_name': 'Hotel'
        },
        'items': [
            {'car_id': 'invalid_id'} 
        ]
    }
    
    # Mock request object (not used in function but passed)
    class MockRequest:
        pass
        
    booking = create_booking_record(order_data, MockRequest())
    
    if booking:
        print(f"✅ SUCCESS: Booking created with ID {booking.id}")
        return True
    else:
        print("❌ FAILURE: Booking returned None")
        return False

if __name__ == '__main__':
    try:
        test_booking_creation()
    except Exception as e:
        print(f"❌ CRASH: {e}")
        import traceback
        traceback.print_exc()
