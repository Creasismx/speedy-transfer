#!/usr/bin/env python
"""
Test script to verify Payment record creation
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from speedy_app.core.models import Payment, Reservation, Booking
from datetime import datetime

print("=" * 60)
print("PAYMENT RECORD TEST")
print("=" * 60)

# Check current state
total_payments = Payment.objects.count()
total_reservations = Reservation.objects.count()
total_bookings = Booking.objects.count()

print(f"\nCurrent Database State:")
print(f"  - Payments: {total_payments}")
print(f"  - Reservations: {total_reservations}")
print(f"  - Bookings: {total_bookings}")

# Get the most recent booking if it exists
if total_bookings > 0:
    recent_booking = Booking.objects.order_by('-date_capture').first()
    print(f"\nMost Recent Booking:")
    print(f"  - ID: {recent_booking.id}")
    print(f"  - Customer: {recent_booking.customer_name}")
    print(f"  - Amount: ${recent_booking.total_amount}")
    print(f"  - Payment Method: {recent_booking.payment_method}")
    print(f"  - Date: {recent_booking.date_capture}")
    
    # Check if this booking has an associated payment record
    # Try to find a reservation with matching email
    matching_reservation = Reservation.objects.filter(email=recent_booking.client_id).first()
    if matching_reservation:
        payments = Payment.objects.filter(reservation=matching_reservation)
        print(f"\n  - Found {payments.count()} payment record(s) for this booking")
        for p in payments:
            print(f"    * Payment ID {p.id}: ${p.amount} via {p.method} on {p.paid_at}")
    else:
        print(f"\n  ⚠️ No Payment record found for this booking")
        print(f"     This means sales reports won't show this transaction!")

print("\n" + "=" * 60)
print("RECOMMENDATION:")
print("=" * 60)
print("If bookings exist but no payments, you need to:")
print("1. Complete a new test booking with payment")
print("2. Or run a migration script to create Payment records for existing bookings")
print("=" * 60)
