import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Define base dir
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env
env_path = BASE_DIR / '.env'
print(f"Loading environment from: {env_path}")
load_dotenv(env_path)

# Check values
mode = os.getenv('PAYPAL_MODE')
client_id = os.getenv('PAYPAL_CLIENT_ID')

print(f"PAYPAL_MODE: '{mode}'")
if client_id:
    print(f"PAYPAL_CLIENT_ID: '{client_id[:5]}...'")
else:
    print("PAYPAL_CLIENT_ID: Not found")

if mode != 'live':
    print("WARNING: Mode is not 'live'. logic in settings.py defaults to 'sandbox' if this is missing or different.")
else:
    print("SUCCESS: Mode is correctly set to 'live' in .env.")
