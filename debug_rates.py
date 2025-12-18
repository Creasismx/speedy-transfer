import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.develop')
django.setup()

from speedy_app.core.models import CarType, Rate, Zone, Hotel, Car

print("--- CAR TYPES ---")
for ct in CarType.objects.all():
    print(f"Code: '{ct.code}', Name: '{ct.name}'")

print("\n--- RATES SUMMARY ---")
# Group rates by Car Type
for ct in CarType.objects.all():
    count = Rate.objects.filter(car__car_type=ct).count()
    print(f"CarType '{ct.code}': {count} rates found")
    if count > 0:
        # Show a few examples
        example = Rate.objects.filter(car__car_type=ct).first()
        try:
            print(f"  Example: Zone {example.zone} -> ${example.price}")
        except Exception:
            print("  Example: (Invalid Zone Link)")

print("\n--- CHECKING SPECIFIC SCENARIO ---")
# User mentioned "THE WESTIN RESORT"
westin = Hotel.objects.filter(name__icontains="Westin").first()
if westin:
    print(f"Found Hotel: {westin.name} (Zone: {westin.zone})")
    if westin.zone:
        rates = Rate.objects.filter(zone=westin.zone)
        print(f"Rates for Zone {westin.zone}:")
        for r in rates:
            print(f"  - {r.car.name} ({r.car.car_type.code}): ${r.price}")
    else:
        print("  Hotel has no Zone assigned!")
else:
    print("Could not find 'Westin' hotel.")
