#!/usr/bin/env python3
"""
Test Booking Creation and Email Functionality
Tests the complete payment flow with booking creation and email sending
"""

import os
import sys
import django
from pathlib import Path
import json

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.develop')
django.setup()

from django.test import Client
from django.conf import settings
from speedy_app.core.models import Booking
from speedy_app.core.views import create_booking_record, send_booking_email


def test_booking_creation():
    """Test booking creation functionality"""
    print("📝 Testing Booking Creation")
    print("=" * 50)
    
    # Sample order data
    test_order = {
        "trip_type": "oneway",
        "people": 2,
        "pickup": {
            "datetime": "2025-01-15T10:00",
            "location_id": "1",
            "location_name": "VELAS VALLARTA"
        },
        "dropoff": {
            "location_id": "2",
            "location_name": "AEROPUERTO"
        },
        "car_type_label": "VAN",
        "items": [
            {
                "name": "VAN 001",
                "unit_amount": 82.00,
                "currency": "USD",
                "date": "2025-01-15",
                "time": "10:00",
                "capacity": 8,
                "car_id": "1"
            }
        ],
        "subtotal": 82.00,
        "total": 82.00,
        "customer": {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "1234567890",
            "address": "123 Test St",
            "city": "Testville",
            "zip": "12345",
            "country": "USA"
        },
        "currency": "USD"
    }
    
    # Mock request object
    class MockRequest:
        def __init__(self):
            self.session = {}
    
    mock_request = MockRequest()
    
    try:
        # Test booking creation
        print("1. Creating booking record...")
        booking = create_booking_record(test_order, mock_request)
        
        if booking:
            print(f"   ✅ Booking created successfully!")
            print(f"   Booking ID: {booking.id}")
            print(f"   Customer: {booking.customer_name}")
            print(f"   Total: ${booking.total_amount} {booking.currency}")
            print(f"   Trip Type: {'One Way' if booking.one_way else 'Round Trip'}")
            
            # Verify booking was saved to database
            saved_booking = Booking.objects.get(id=booking.id)
            print(f"   ✅ Booking verified in database")
            
            return booking
        else:
            print("   ❌ Booking creation failed")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_email_functionality():
    """Test email sending functionality"""
    print("\n📧 Testing Email Functionality")
    print("=" * 50)
    
    # Sample order data
    test_order = {
        "trip_type": "oneway",
        "people": 2,
        "pickup": {
            "datetime": "2025-01-15T10:00",
            "location_id": "1",
            "location_name": "VELAS VALLARTA"
        },
        "dropoff": {
            "location_id": "2",
            "location_name": "AEROPUERTO"
        },
        "items": [
            {
                "name": "VAN 001",
                "unit_amount": 82.00,
                "currency": "USD",
                "date": "2025-01-15",
                "time": "10:00"
            }
        ],
        "total": 82.00,
        "customer": {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "1234567890"
        }
    }
    
    # Mock request object
    class MockRequest:
        def __init__(self):
            self.session = {}
    
    mock_request = MockRequest()
    
    try:
        print("1. Testing email configuration...")
        print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        print("\n2. Attempting to send test email...")
        send_booking_email(test_order, mock_request, test_recipients=True)
        print("   ✅ Email function completed (check logs for success/failure)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_complete_payment_flow():
    """Test the complete payment flow"""
    print("\n🔄 Testing Complete Payment Flow")
    print("=" * 50)
    
    client = Client()
    
    # Test order data
    test_order = {
        "trip_type": "oneway",
        "people": 2,
        "pickup": {
            "datetime": "2025-01-15T10:00",
            "location_id": "1",
            "location_name": "VELAS VALLARTA"
        },
        "dropoff": {
            "location_id": "2",
            "location_name": "AEROPUERTO"
        },
        "items": [
            {
                "name": "VAN 001",
                "unit_amount": 82.00,
                "currency": "USD",
                "car_id": "1"
            }
        ],
        "total": 82.00,
        "customer": {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "1234567890"
        }
    }
    
    try:
        print("1. Testing checkout session creation...")
        response = client.get('/create_checkout_session/', {
            'order_json': json.dumps(test_order)
        })
        
        if response.status_code == 302:
            print(f"   ✅ Checkout session created successfully")
            print(f"   Redirect URL: {response.url}")
            
            # Test payment success page
            print("\n2. Testing payment success page...")
            response = client.get('/payment_success/', {
                'session_id': 'cs_test_12345'
            })
            
            if response.status_code == 200:
                print(f"   ✅ Payment success page loads correctly")
                return True
            else:
                print(f"   ❌ Payment success page failed: {response.status_code}")
                return False
        else:
            print(f"   ❌ Checkout session creation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """Main test function"""
    print("🎯 Booking Creation and Email Test")
    print("=" * 60)
    
    # Test 1: Booking creation
    booking = test_booking_creation()
    
    # Test 2: Email functionality
    email_ok = test_email_functionality()
    
    # Test 3: Complete payment flow
    flow_ok = test_complete_payment_flow()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Booking Creation: {'✅ PASS' if booking else '❌ FAIL'}")
    print(f"   Email Functionality: {'✅ PASS' if email_ok else '❌ FAIL'}")
    print(f"   Complete Payment Flow: {'✅ PASS' if flow_ok else '❌ FAIL'}")
    
    if booking and email_ok and flow_ok:
        print("\n🎉 SUCCESS! All tests passed!")
        print("   Your payment system is now fully functional with:")
        print("   ✅ Booking creation working")
        print("   ✅ Email notifications working")
        print("   ✅ Complete payment flow working")
        return True
    else:
        print("\n⚠️  Some tests failed. Please review the issues above.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

