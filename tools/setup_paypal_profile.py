import os
import sys
import paypalrestsdk
from dotenv import load_dotenv
from pathlib import Path

# Setup Environment
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# Configure PayPal
paypalrestsdk.configure({
    "mode": os.getenv('PAYPAL_MODE', 'sandbox'),
    "client_id": os.getenv('PAYPAL_CLIENT_ID'),
    "client_secret": os.getenv('PAYPAL_SECRET')
})

print(f"Configured PayPal Mode: {os.getenv('PAYPAL_MODE')}")
print(f"Client ID: {os.getenv('PAYPAL_CLIENT_ID')[:10]}...")

def list_and_create_profile():
    print("\n--- Existing Web Profiles ---")
    try:
        profiles = paypalrestsdk.WebProfile.all()
        # Debug: Print what we got
        print(f"DEBUG: Type of profiles: {type(profiles)}")
        if hasattr(profiles, 'error'):
            print(f"DEBUG: Error in profiles object: {profiles.error}")
            
        found_v4 = False
        try:
            # Check if profiles is iterable
            for p in profiles:
                print(f"ID: {p.id}, Name: {p.name}")
                if p.name == "SpeedyTransfers_GuestCheckout_v4":
                    found_v4 = True
                    print(f"   >>> FOUND V4 PROFILE: {p.id}")
                    # Print details of v4
                    try:
                        print(f"   Settings: {p.to_dict()}")
                    except:
                        pass
        except Exception as iter_err:
            print(f"WARNING: Could not iterate profiles: {iter_err}")
            # If we can't iterate, we assume we need to create it, OR there is an auth error
            if isinstance(profiles, dict) and 'name' in profiles and profiles['name'] == 'INTERNAL_SERVICE_ERROR':
                 print("CRITICAL: PayPal internal error.")
            

        if not found_v4:
            print("\nWARN: V4 Profile NOT found (or list failed). Creating it now...")
            create_v4_profile()
        else:
            print("\nSUCCESS: V4 Profile already exists.")

    except Exception as e:
        print(f"ERROR listing profiles: {e}")
        import traceback
        traceback.print_exc()

def create_v4_profile():
    print("Attempting to create V4 profile...")
    web_profile = paypalrestsdk.WebProfile({
        "name": "SpeedyTransfers_GuestCheckout_v4",
        "presentation": {
            "brand_name": "Speedy Transfers",
            "locale_code": "MX"
        },
        "input_fields": {
            "allow_note": True,
            "no_shipping": 1,
            "address_override": 0
        },
        "flow_config": {
            "landing_page_type": "Billing",
            "bank_txn_pending_url": "https://www.speedytransfers.mx/",
            "user_action": "commit"
        }
    })

    if web_profile.create():
        print(f"SUCCESS: Created New Web Profile v4: {web_profile.id}")
    else:
        print(f"FAIL: Failed to create profile: {web_profile.error}")

if __name__ == "__main__":
    list_and_create_profile()
