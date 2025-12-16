import requests
import json
import os

def make_paypal_payment(amount, currency, return_url, cancel_url):
    # Set up PayPal API credentials
    client_id = os.getenv("PAYPAL_ID")
    secret = os.getenv("PAYPAL_SECRET")
    url = os.getenv("PAYPAL_BASE_URL")
    # Set up API endpoints
    base_url = url
    token_url = base_url + '/v1/oauth2/token'
    payment_url = base_url + '/v1/payments/payment'

    # Request an access token
    token_payload = {'grant_type': 'client_credentials'}
    token_headers = {'Accept': 'application/json', 'Accept-Language': 'en_US'}
    token_response = requests.post(token_url, auth=(client_id, secret), data=token_payload, headers=token_headers)

    if token_response.status_code != 200:
        return False,"Failed to authenticate with PayPal API",None

    access_token = token_response.json()['access_token']

    # Create payment payload
    payment_payload = {
        'intent': 'sale',
        'payer': {'payment_method': 'paypal'},
        'transactions': [{
            'amount': {'total': str(amount), 'currency': currency},
            'description': 'Vulnvision scan & protect '
        }],
        'redirect_urls': {
            'return_url': return_url,
            'cancel_url': cancel_url
        }
    }

    # Create payment request
    payment_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    payment_response = requests.post(payment_url, data=json.dumps(payment_payload), headers=payment_headers)
    print(payment_response.text)
    if payment_response.status_code != 201:
        return False , 'Failed to create PayPal payment.',None

    payment_id = payment_response.json()['id']
    approval_url = next(link['href'] for link in payment_response.json()['links'] if link['rel'] == 'approval_url')

    return True,payment_id, approval_url


def verify_paypal_payment(payment_id):
    # Set up PayPal API credentials
    client_id = os.getenv("PAYPAL_ID")
    secret = os.getenv("PAYPAL_SECRET")
    url = os.getenv("PAYPAL_BASE_URL")

    # Set up API endpoints
    base_url = url
    token_url = base_url + '/v1/oauth2/token'
    payment_url = base_url + '/v1/payments/payment'

    # Request an access token
    token_payload = {'grant_type': 'client_credentials'}
    token_headers = {'Accept': 'application/json', 'Accept-Language': 'en_US'}
    token_response = requests.post(token_url, auth=(client_id, secret), data=token_payload, headers=token_headers)

    if token_response.status_code != 200:
        raise Exception('Failed to authenticate with PayPal API.')

    access_token = token_response.json()['access_token']

    # Retrieve payment details
    payment_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    payment_details_url = f'{payment_url}/{payment_id}'
    payment_details_response = requests.get(payment_details_url, headers=payment_headers)

    if payment_details_response.status_code != 200:
        raise Exception('Failed to retrieve PayPal payment details.')

    payment_status = payment_details_response.json()['state']
    if payment_status == 'approved':
        # Payment is successful, process the order
        # Retrieve additional payment details if needed
        payer_email = payment_details_response.json()['payer']['payer_info']['email']
        # ... process the order ...
        return True
    else:
        # Payment failed or was canceled
        return False

def booking_to_order_data(booking):
    """
    Reconstructs the order dictionary from a Booking model instance.
    This allows us to reuse the existing email and template logic.
    """
    if not booking:
        return None
        
    order_data = {
        'total': float(booking.total_amount) if booking.total_amount else 0,
        'currency': booking.currency,
        'payment_method': booking.payment_method,
        'trip_type': booking.trip_type,
        'people': booking.how_people,
        'customer': {
            'email': booking.client_id,
            'name': booking.customer_name,
            'first_name': booking.customer_first_name,
            'last_name': booking.customer_last_name,
            'phone': booking.customer_phone,
            'address': booking.customer_address,
            'city': booking.customer_city,
            'state': booking.customer_state,
            'zip': booking.customer_zip,
            'country': booking.customer_country,
            'company': booking.customer_company,
            'passport_number': booking.customer_passport_number,
            'emergency_contact_name': booking.emergency_contact_name,
            'emergency_contact_phone': booking.emergency_contact_phone,
            'special_instructions': booking.special_instructions,
            'additional_notes': booking.additional_notes,
            # Handle date of birth conversion safely
            'date_of_birth': booking.customer_date_of_birth.strftime('%Y-%m-%d') if booking.customer_date_of_birth else '',
        },
        'pickup': {
            'location_name': booking.pickup_location1.name if booking.pickup_location1 else 'Selected Location',
            'datetime': booking.pickup_date_time.isoformat() if booking.pickup_date_time else '',
        },
        'dropoff': {
            'location_name': booking.dropoff_location1.name if booking.dropoff_location1 else 'Selected Location',
            'datetime': booking.pickup_date_time.isoformat() if booking.pickup_date_time else '', # Using pickup time as base
        },
        'items': [
            {
                'name': booking.car_id.name if booking.car_id else 'Vehicle',
                'capacity': booking.car_id.max if booking.car_id else 0,
                'unit_amount': float(booking.total_amount) if booking.total_amount else 0,
                'currency': booking.currency,
                'date': booking.pickup_date_time.strftime('%Y-%m-%d') if booking.pickup_date_time else '',
                'time': booking.pickup_date_time.strftime('%H:%M') if booking.pickup_date_time else '',
            }
        ]
    }
    
    # Handle return trip
    if booking.trip_type == 'roundtrip' and booking.return_date_time:
        order_data['return_trip'] = {
            'pickup_location_name': booking.pickup_location2.name if booking.pickup_location2 else 'Selected Location',
            'dropoff_location_name': booking.dropoff_location2.name if booking.dropoff_location2 else 'Selected Location',
            'datetime': booking.return_date_time.isoformat(),
        }
        
    return order_data