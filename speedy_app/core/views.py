# First, you need to import the Hotel and Car models at the top of your file
from .models import Zone, Contact, Car, Hotel, Rate  # Added Rate for the price lookup

import paypalrestsdk
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import HttpResponse
#from .utils import make_paypal_payment, verify_paypal_payment
#import paypalrestsdk
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
import stripe  # new
from django.templatetags.static import static
from urllib.parse import quote
import os
import json

#For sending mail uppong form submission
from django.core.mail import send_mail

# Updated import to include EmailMessage and EmailMultiAlternatives
from django.core.mail import send_mail, EmailMultiAlternatives


paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET,
})


# Optional: define your return/cancel URLs here or in settings
#PAYPAL_RETURN_URL = "https://example.com/payment/paypal/success/"
#PAYPAL_CANCEL_URL = "https://example.com/payment/paypal/cancel/"

class LandingView(TemplateView):
    template_name = "speedy_app/landing_page.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get zones with hotels for location dropdowns
        context['zones_with_hotels'] = Zone.objects.prefetch_related('hotels').all()
        
        # FIXED: Get car types as choices for the dropdown
        # This matches what your template expects: car_types
        context['car_types'] = Car.CAR_TYPES
        
        # Optional: Keep cars_by_type if needed elsewhere
        cars = Car.objects.all().order_by('type')
        cars_by_type = {}
        
        for car in cars:
            if car.type not in cars_by_type:
                cars_by_type[car.type] = []
            cars_by_type[car.type].append(car)
        
        context['cars_by_type'] = cars_by_type
        
        # Populate form fields from GET parameters
        query = self.request.GET
        context.update({
            'pickup_datetime': query.get('pickup_datetime', ''),
            'pickup_location': query.get('pickup_location', ''),
            'dropoff_location': query.get('dropoff_location', ''),
            'return_datetime': query.get('return_datetime', ''),
            'people': query.get('people', ''),
            'car_type': query.get('car_type', ''),
            'trip_type': query.get('trip_type', 'oneway')
        })
        
        return context


class ResultsView(TemplateView):
    template_name = "speedy_app/results_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # CRITICAL FIX: Use the same context key as LandingView
        # Template expects 'zones_with_hotels', not 'zones'
        context['zones_with_hotels'] = Zone.objects.prefetch_related('hotels').all()
        context['cars'] = Car.objects.all()
        context['car_types'] = Car.CAR_TYPES
        
        # Extract GET parameters (submitted form data) - ALL OF THEM
        query = self.request.GET
        pickup_location_id = query.get('pickup_location', '')
        dropoff_location_id = query.get('dropoff_location', '')
        car_type_id = query.get('car_type', '')
        
        # DEBUG: Print what we received
        print(f"\n=== DEBUG RESULTS VIEW ===")
        print(f"Query params: {dict(query)}")
        print(f"Pickup Location ID: {pickup_location_id}")
        print(f"Car Type ID: {car_type_id}")
        
        # CRITICAL FIX: Pass ALL form data to preserve state
        context['pickup_datetime'] = query.get('pickup_datetime', '')
        context['pickup_location'] = pickup_location_id
        context['dropoff_location'] = dropoff_location_id
        context['return_datetime'] = query.get('return_datetime', '')
        context['return_pickup_location'] = query.get('return_pickup_location', '')
        context['return_dropoff_location'] = query.get('return_dropoff_location', '')
        context['people'] = query.get('people', '')
        context['car_type'] = car_type_id
        context['trip_type'] = query.get('trip_type', 'oneway')
        
        # Get trip_type from the form and convert it to the database format
        trip_type_form = query.get('trip_type', 'oneway')
        if trip_type_form == 'oneway':
            travel_type_db = 'ONE_WAY'
        elif trip_type_form == 'roundtrip':
            travel_type_db = 'ROUND_TRIP'
        else:
            travel_type_db = 'ONE_WAY'

        # LOGIC: Each Car row represents one unit; create one option per rate/car
        transfer_options = []
        
        # DEBUG: Check if we have the required parameters
        if not pickup_location_id:
            print("ERROR: No pickup_location_id provided")
        if not car_type_id:
            print("ERROR: No car_type_id provided")
            
        if pickup_location_id and car_type_id:
            try:
                # Get the hotel to find its zone_id
                print(f"Looking for hotel with ID: {pickup_location_id}")
                pickup_hotel = Hotel.objects.get(id=pickup_location_id)
                zone_id = pickup_hotel.zone_id
                print(f"Found hotel: {pickup_hotel.name}, Zone ID: {zone_id}")

                # Filter Rate based on car TYPE, zone_id, and the dynamically determined travel_type
                print(f"Looking for rates with car_type={car_type_id}, zone_id={zone_id}, travel_type={travel_type_db}")
                rates = Rate.objects.filter(
                    car__type=car_type_id,
                    zone_id=zone_id,
                    travel_type=travel_type_db
                )
                print(f"Found {rates.count()} rates")

                # Generate one vehicle option per rate (since each Car row is a single unit)
                for rate in rates:
                    car = rate.car

                    # Resolve image URL robustly
                    image_url = None
                    try:
                        # Use MEDIA url only if the underlying file actually exists
                        if car.image and getattr(car.image, 'name', None):
                            file_name = car.image.name
                            try:
                                if car.image.storage.exists(file_name):
                                    image_url = car.image.url
                            except Exception:
                                image_url = None
                    except Exception:
                        image_url = None

                    if not image_url:
                        # Try to use the raw value as absolute URL or as a static filename
                        raw_value = None
                        try:
                            raw_value = car.image.name if car.image else None
                        except Exception:
                            raw_value = None
                        if raw_value:
                            raw_value = raw_value.strip()
                            if raw_value.lower().startswith(("http://", "https://", "//")):
                                image_url = raw_value
                            else:
                                basename = os.path.basename(raw_value)
                                if "." not in basename:
                                    basename = f"{basename}.jpg"
                                image_url = static(f"images/cars/{quote(basename)}")

                    # Name-based defaults
                    if not image_url and car.name:
                        upper_name = car.name.upper()
                        if "VAN-DARK" in upper_name:
                            image_url = static("images/cars/Van_Dark.jpg")
                        elif "STANDARD-VAN" in upper_name:
                            image_url = static("images/cars/Standard_Van.jpg")
                        elif "LUXURY-VAN" in upper_name:
                            image_url = static("images/cars/Luxury_Van.jpg")
                        elif upper_name.startswith("HIACE-VAN-"):
                            # Try to map HIACE-VAN-00X to Hiace_White_00X.jpg
                            suffix = upper_name.split("HIACE-VAN-")[-1]
                            candidate = f"Hiace_White_{suffix}.jpg"
                            image_url = static(f"images/cars/{quote(candidate)}")
                        elif "ECONOMY-SEDAN" in upper_name:
                            image_url = static("images/cars/Economy_Sedan.jpg")
                        elif "PREMIUM-SEDAN" in upper_name:
                            image_url = static("images/cars/Premium_Sedan.jpg")
                        elif "COMPACT-SUV" in upper_name:
                            image_url = static("images/cars/Compact_SUV.jpg")
                        elif "MIDSIZE-SUV" in upper_name:
                            image_url = static("images/cars/Midsize_SUV.jpg")
                        elif "LUXURY-SUV" in upper_name:
                            image_url = static("images/cars/Luxury_SUV.jpg")
                        elif "MINI-SPRINTER" in upper_name:
                            image_url = static("images/cars/Mini_Sprinter.jpg")
                        elif "STANDARD-SPRINTER" in upper_name:
                            image_url = static("images/cars/Standard_Sprinter.jpg")
                        elif "LUXURY-SPRINTER" in upper_name:
                            image_url = static("images/cars/Luxury_Sprinter.jpg")
                        elif "EXECUTIVE-SPRINTER" in upper_name:
                            image_url = static("images/cars/Executive_Sprinter.jpg")
                        elif "MINI-BUS" in upper_name:
                            image_url = static("images/cars/Mini_Bus.jpg")
                        elif "LUXURY-MINI-BUS" in upper_name:
                            image_url = static("images/cars/Luxury_Mini_Bus.jpg")
                        elif "PARTY-BUS" in upper_name:
                            image_url = static("images/cars/Party_Bus.jpg")
                        elif "TOUR-BUS" in upper_name:
                            image_url = static("images/cars/Tour_Bus.jpg")
                        elif "CHARTER-BUS" in upper_name:
                            image_url = static("images/cars/Charter_Bus.jpg")
                        elif "LIMOUSINE" in upper_name:
                            if "STRETCH" in upper_name:
                                image_url = static("images/cars/Stretch_Limousine.jpg")
                            else:
                                image_url = static("images/cars/Luxury_Limousine.jpg")
                        elif "HUMMER-LIMO" in upper_name:
                            image_url = static("images/cars/Hummer_Limo.jpg")
                        elif upper_name.startswith("SPRINTER-MB-"):
                            suffix = upper_name.split("SPRINTER-MB-")[-1]
                            candidate = f"Mercedes_Sprinter_{suffix}.jpg"
                            image_url = static(f"images/cars/{quote(candidate)}")
                        elif upper_name.startswith("PILOT-HP-"):
                            suffix = upper_name.split("PILOT-HP-")[-1]
                            candidate = f"Honda_Pilot_{suffix}.jpg"
                            image_url = static(f"images/cars/{quote(candidate)}")
                        elif upper_name.startswith("TRANSIT-FT-"):
                            suffix = upper_name.split("TRANSIT-FT-")[-1]
                            candidate = f"Ford_Transit_{suffix}.jpg"
                            image_url = static(f"images/cars/{quote(candidate)}")
                        elif upper_name.startswith("SUBURBAN-"):
                            suffix = upper_name.split("SUBURBAN-")[-1]
                            if suffix in ("101", "102"):
                                candidate = f"Suburban_Black_{suffix}.jpg"
                            else:
                                candidate = f"Suburban_White_{suffix}.jpg"
                            image_url = static(f"images/cars/{quote(candidate)}")

                    # Type-based defaults
                    if not image_url:
                        default_per_type = {
                            'VAN': 'Van_Dark.jpg',
                            'SPRINTER': 'Small_Sprinter.jpg',
                            'SUV': 'Midsize_SUV.jpg',
                            'BUS': 'Mini_Bus.jpg',
                            'SEDAN': 'Economy_Sedan.jpg',
                        }
                        default_name = default_per_type.get(car.type)
                        if default_name:
                            image_url = static(f"images/cars/{quote(default_name)}")

                    print(f"Image resolved for car '{car.name}': {image_url}")
                    
                    # One option per vehicle unit
                    unique_id = f"{rate.id}"
                    vehicle_name = car.name

                    transfer_options.append({
                        'id': unique_id,
                        'rate_id': rate.id,
                        'car_id': car.id,
                        'unit_number': 1,
                        'car_name': vehicle_name,
                        'car_description': car.description,
                        'car_capacity': car.max,
                        'image_url': image_url,
                        'price': rate.price,
                        'travel_type': rate.travel_type,
                        'departure_date': context['pickup_datetime'].split('T')[0] if context['pickup_datetime'] else '',
                        'departure_time': context['pickup_datetime'].split('T')[1] if context['pickup_datetime'] else '',
                        'availability_status': 'available',
                        'total_fleet_size': 1,
                        'is_fleet_vehicle': False,
                    })

                    print(f"Created transfer option: {unique_id} - {vehicle_name}")

            except Hotel.DoesNotExist:
                print(f"ERROR: Hotel with ID {pickup_location_id} not found.")
            except Car.DoesNotExist:
                print(f"ERROR: Car with ID {car_type_id} not found.")
            except Exception as e:
                print(f"ERROR generating transfer options: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"Final transfer_options count: {len(transfer_options)}")
        context['transfer_options'] = transfer_options
        
        return context

class SummaryView(TemplateView):
    template_name = "speedy_app/summary_page.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['zones'] = Zone.objects.all()
        # FIX: Added cars context for dropdown
        context['cars'] = Car.objects.all() 
        return context    

class CheckoutView(TemplateView):
    template_name = "speedy_app/checkout_page.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['zones'] = Zone.objects.all()
        # FIX: Added cars context for dropdown
        context['cars'] = Car.objects.all()
        return context    

# speedy_app/core/views.py

from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail # Make sure this is imported

# ... (other imports and views)

# Contact Form View 
def contact_form_view(request):
    """
    Handles the contact form submission.
    Saves the form data to the database and sends a multi-part email
    with both a plain text and a well-formatted HTML body.
    """
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        country = request.POST.get("country")
        company = request.POST.get("company")
        interested_in = request.POST.get("interested")
        message = request.POST.get("additional")

        # Save to database
        try:
            Contact.objects.create(
                name=name,
                email=email,
                phone=phone,
                country=country,
                company=company,
                interested_in=interested_in,
                message=message,
            )
        except Exception as e:
            print(f"Error saving contact form to database: {e}")
            messages.error(request, "There was an error saving your message. Please try again.")
            return redirect(reverse('core:home_view'))

        # --- EMAIL SENDING LOGIC ---
        try:
            # Create a clean, HTML body for the email with inline styles
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
                    h2 {{ color: #047884; }}
                    p {{ margin: 0 0 10px; }}
                    strong {{ color: #333; }}
                    .footer {{ margin-top: 20px; font-size: 0.9em; color: #888; }}
                    .data-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    .data-table th, .data-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                    .data-table th {{ background-color: #f4f4f4; color: #555; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>New Contact Form Submission</h2>
                    <p>A new message has been submitted through the website's contact form. Here are the details:</p>
                    
                    <table class="data-table">
                        <tr>
                            <th>Name:</th>
                            <td>{name}</td>
                        </tr>
                        <tr>
                            <th>Email:</th>
                            <td>{email}</td>
                        </tr>
                        <tr>
                            <th>Phone:</th>
                            <td>{phone}</td>
                        </tr>
                        <tr>
                            <th>Country:</th>
                            <td>{country}</td>
                        </tr>
                        <tr>
                            <th>Company:</th>
                            <td>{company}</td>
                        </tr>
                        <tr>
                            <th>Interested In:</th>
                            <td>{interested_in}</td>
                        </tr>
                        <tr>
                            <th>Message:</th>
                            <td>{message}</td>
                        </tr>
                    </table>
                    
                    <p class="footer">This email was sent automatically from the website contact form.</p>
                </div>
            </body>
            </html>
            """
            text_body = f"""
            New Contact Form Submission\n\n
            Name: {name}
            Email: {email}
            Phone: {phone}
            Country: {country}
            Company: {company}
            Interested In: {interested_in}
            Message: {message}
            """

            subject = "New Contact Form Submission"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = ['cmelendezgp@gmail.com']

            # Use EmailMultiAlternatives to send both HTML and plain text versions
            msg = EmailMultiAlternatives(subject, text_body, from_email, recipient_list)
            msg.attach_alternative(html_body, "text/html")
            msg.send()

        except Exception as e:
            print(f"Error sending contact email: {e}")
            messages.error(request, "Your message was saved, but there was an error sending the email notification.")
        
        messages.success(request, "Your message has been submitted successfully!")
        
        return redirect(reverse('core:home_view'))

    return HttpResponse("Invalid request", status=400)


def create_payment(request):
    # Accept an optional order_json to set amount and description for testing
    order_json = request.POST.get('order_json')
    amount_total = "10.00"
    description = "Payment for Product/Service"
    if order_json:
        try:
            order = json.loads(order_json)
            total = float(order.get('total', 0))
            amount_total = f"{total:.2f}"
            description = f"Transfer booking ({order.get('trip_type', 'oneway')})"
        except Exception:
            pass

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal",
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('core:execute_payment')),
            "cancel_url": request.build_absolute_uri(reverse('core:payment_failed')),
        },
        "transactions": [
            {
                "amount": {
                    "total": amount_total,  # Total amount in USD
                    "currency": "USD",
                },
                "description": description,
            }
        ],
    })

    if payment.create():
        # Store order JSON in session
        request.session['order_json'] = order_json
        return redirect(payment.links[1].href)  # Redirect to PayPal for payment
    else:
        return render(request, 'speedy_app/payment_failed.html')

def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Retrieve order JSON from session
        order_json = request.session.get('order_json')
        # Get order data for display and create booking
        order_data = None
        booking_id = None
        
        if order_json:
            try:
                order = json.loads(order_json)
                order_data = order
                # Add payment method information
                order['payment_method'] = 'PayPal'
                # Create booking record in database
                booking = create_booking_record(order, request)
                if booking:
                    booking_id = booking.id
                # Send booking email to the guest
                send_booking_email(order, request)
                # Send booking email to test recipients
                send_booking_email(order, request, test_recipients=True)
            except Exception as e:
                print(f"Error processing successful PayPal payment: {e}")
                import traceback
                traceback.print_exc()
        
        context = {
            'order_data': order_data,
            'booking_id': booking_id,
        }
        
        return render(request, 'speedy_app/payment_success.html', context)
    else:
        return render(request, 'speedy_app/payment_failed.html')

def payment_checkout(request):
    return render(request, 'speedy_app/checkout.html')

def payment_failed(request):
    return render(request, 'speedy_app/payment_failed.html')

def payment_success(request):
    # On successful payment, attempt to send booking emails using stored order
    order_data = None
    booking_id = None
    
    try:
        order_json = request.session.get('order_json')
        if order_json:
            order = json.loads(order_json)
            order_data = order
            # Add payment method information
            order['payment_method'] = 'Stripe'
            # Create booking record in database
            booking = create_booking_record(order, request)
            if booking:
                booking_id = booking.id
            # Send booking emails
            send_booking_email(order, request)
            send_booking_email(order, request, test_recipients=True)
            # Don't delete session data yet - we need it for display
    except Exception as e:
        print(f"Error during payment_success handling: {e}")
        import traceback
        traceback.print_exc()
    
    # Clear session data after processing
    try:
        if 'order_json' in request.session:
            del request.session['order_json']
    except Exception:
        pass
    
    context = {
        'order_data': order_data,
        'booking_id': booking_id,
    }
    
    return render(request, 'speedy_app/payment_success.html', context)

from django.shortcuts import redirect

def create_checkout_session(request):
    if request.method == 'GET':
        # Use the current domain for redirects
        success_absolute = request.build_absolute_uri(reverse('core:payment_success'))
        cancel_absolute = request.build_absolute_uri(reverse('core:payment_failed'))
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Build line_items from optional order_json
            order_json = request.GET.get('order_json')
            line_items = []
            if order_json:
                try:
                    # Persist order for later email sending on success
                    request.session['order_json'] = order_json
                    order = json.loads(order_json)
                    for item in order.get('items', []):
                        amount_cents = int(round(float(item.get('unit_amount', 0)) * 100))
                        name = item.get('name', 'Transfer')
                        desc_date = item.get('date', '')
                        desc_time = item.get('time', '')
                        description = f"{desc_date} {desc_time}".strip()
                        line_items.append({
                            'price_data': {
                                'currency': 'usd',
                                'unit_amount': amount_cents,
                                'product_data': {
                                    'name': name,
                                    'description': description or name,
                                }
                            },
                            'quantity': 1
                        })
                except Exception:
                    line_items = []

            if not line_items:
                # fallback demo item
                line_items = [
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': 2000,
                            'product_data': {
                                'name': 'Transfer',
                                'description': 'Test checkout session'
                            }
                        },
                        'quantity': 1
                    }
                ]
            checkout_session = stripe.checkout.Session.create(
                success_url=f"{success_absolute}?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=cancel_absolute,
                payment_method_types=['card'],
                mode='payment',
                line_items=line_items
            )
            return redirect(checkout_session.url)  # ✅ Redirect to Stripe Checkout
        except Exception as e:
            return JsonResponse({'error': str(e)})

def create_booking_record(order, request):
    """
    Creates a booking record in the database from the order data.
    """
    try:
        from .models import Booking, Hotel, Car
        from datetime import datetime, timedelta
        
        # Parse datetime strings
        pickup_datetime = None
        return_datetime = None
        
        if order.get('pickup', {}).get('datetime'):
            try:
                pickup_datetime = datetime.fromisoformat(order['pickup']['datetime'].replace('Z', '+00:00'))
            except:
                pickup_datetime = datetime.now()
        
        if order.get('return_trip') and order.get('return_trip', {}).get('datetime'):
            try:
                return_datetime = datetime.fromisoformat(order['return_trip']['datetime'].replace('Z', '+00:00'))
            except:
                return_datetime = datetime.now()
        else:
            # For one-way trips, set return time to pickup time + 2 hours
            return_datetime = pickup_datetime + timedelta(hours=2) if pickup_datetime else datetime.now()
        
        # Get or create customer ID (using email as unique identifier)
        customer_email = order.get('customer', {}).get('email', '')
        if not customer_email:
            customer_email = f"guest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Try to find hotels by name if location_id is not available
        pickup_location1 = None
        dropoff_location1 = None
        pickup_location2 = None
        dropoff_location2 = None
        
        try:
            if order.get('pickup', {}).get('location_id'):
                pickup_location1 = Hotel.objects.get(id=order['pickup']['location_id'])
            elif order.get('pickup', {}).get('location_name'):
                pickup_location1 = Hotel.objects.filter(name__icontains=order['pickup']['location_name']).first()
            
            if order.get('dropoff', {}).get('location_id'):
                dropoff_location1 = Hotel.objects.get(id=order['dropoff']['location_id'])
            elif order.get('dropoff', {}).get('location_name'):
                dropoff_location1 = Hotel.objects.filter(name__icontains=order['dropoff']['location_name']).first()
            
            if order.get('return_trip'):
                if order['return_trip'].get('pickup_location_id'):
                    pickup_location2 = Hotel.objects.get(id=order['return_trip']['pickup_location_id'])
                elif order['return_trip'].get('pickup_location_name'):
                    pickup_location2 = Hotel.objects.filter(name__icontains=order['return_trip']['pickup_location_name']).first()
                
                if order['return_trip'].get('dropoff_location_id'):
                    dropoff_location2 = Hotel.objects.get(id=order['return_trip']['dropoff_location_id'])
                elif order['return_trip'].get('dropoff_location_name'):
                    dropoff_location2 = Hotel.objects.filter(name__icontains=order['return_trip']['dropoff_location_name']).first()
        except Exception as e:
            print(f"Error finding hotel locations: {e}")
        
        # Try to find car by type
        car_type = None
        try:
            if order.get('items') and len(order['items']) > 0:
                car_id = order['items'][0].get('car_id')
                if car_id:
                    car_type = Car.objects.get(id=car_id)
                else:
                    # Fallback to first available car
                    car_type = Car.objects.first()
        except Exception as e:
            print(f"Error finding car: {e}")
            car_type = Car.objects.first()
        
        # Create the booking record
        booking = Booking.objects.create(
            # Customer Information
            client_id=customer_email,
            customer_name=order.get('customer', {}).get('name', ''),
            customer_phone=order.get('customer', {}).get('phone', ''),
            customer_address=order.get('customer', {}).get('address', ''),
            customer_city=order.get('customer', {}).get('city', ''),
            customer_zip=order.get('customer', {}).get('zip', ''),
            customer_country=order.get('customer', {}).get('country', ''),
            customer_company=order.get('customer', {}).get('company', ''),
            
            # Trip Information
            pickup_location1_id=pickup_location1.id if pickup_location1 else None,
            dropoff_location1_id=dropoff_location1.id if dropoff_location1 else None,
            pickup_location2_id=pickup_location2.id if pickup_location2 else None,
            dropoff_location2_id=dropoff_location2.id if dropoff_location2 else None,
            pickup_date_time=pickup_datetime or datetime.now(),
            return_date_time=return_datetime or datetime.now(),
            car_id=car_type,
            how_people=order.get('people', 1),
            one_way=order.get('trip_type') != 'roundtrip',
            
            # Payment Information
            total_amount=order.get('total', 0),
            currency=order.get('currency', 'USD'),
            payment_method=order.get('payment_method', ''),
            trip_type=order.get('trip_type', 'oneway')
        )
        
        print(f"Booking record created successfully: {booking}")
        return booking
        
    except Exception as e:
        print(f"Error creating booking record: {e}")
        import traceback
        traceback.print_exc()
        return None


def send_booking_email(order, request, test_recipients=False):
    """
    Sends a booking confirmation email to the guest and/or test recipients.
    """
    try:
        # Pull structured fields
        customer = order.get('customer', {}) or {}
        guest_name = customer.get('name') or 'Guest'
        guest_email = customer.get('email') or ''
        guest_phone = customer.get('phone') or ''
        guest_address = customer.get('address') or ''
        guest_city = customer.get('city') or ''
        guest_zip = customer.get('zip') or ''

        trip_type = (order.get('trip_type') or '').upper()
        people = order.get('people') or 0
        pickup = order.get('pickup', {}) or {}
        dropoff = order.get('dropoff', {}) or {}
        return_trip = order.get('return_trip') or None
        car_type_label = order.get('car_type_label') or order.get('car_type_value') or ''
        items = order.get('items') or []
        total = order.get('total') or 0

        # Build items rows
        items_rows_html = ''
        for it in items:
            nm = it.get('name', 'Vehicle')
            dt = it.get('date', '')
            tm = it.get('time', '')
            cp = it.get('capacity', '')
            ua = it.get('unit_amount', 0)
            curr = it.get('currency', 'USD')
            items_rows_html += f"<tr><td>{nm}</td><td>{dt} {tm}</td><td>{cp}</td><td>{ua:.2f} {curr}</td></tr>"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 700px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
                h2 {{ color: #047884; }}
                p {{ margin: 0 0 10px; }}
                strong {{ color: #333; }}
                .section {{ margin-top: 20px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                th {{ background: #f7f7f7; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Booking Confirmation</h2>
                <div class="section">
                    <h3>Customer</h3>
                    <table>
                        <tr><th>Name</th><td>{guest_name}</td></tr>
                        <tr><th>Email</th><td>{guest_email}</td></tr>
                        <tr><th>Phone</th><td>{guest_phone}</td></tr>
                        <tr><th>Address</th><td>{guest_address}</td></tr>
                        <tr><th>City</th><td>{guest_city}</td></tr>
                        <tr><th>ZIP</th><td>{guest_zip}</td></tr>
                    </table>
                </div>
                <div class="section">
                    <h3>Trip</h3>
                    <table>
                        <tr><th>Trip Type</th><td>{trip_type}</td></tr>
                        <tr><th>People</th><td>{people}</td></tr>
                        <tr><th>Pickup</th><td>{pickup.get('datetime','')} — {pickup.get('location_name','')}</td></tr>
                        <tr><th>Dropoff</th><td>{dropoff.get('location_name','')}</td></tr>
                        {f"<tr><th>Return</th><td>{(return_trip or {}).get('datetime','')} — {(return_trip or {}).get('pickup_location_name','')} → {(return_trip or {}).get('dropoff_location_name','')}</td></tr>" if return_trip else ''}
                        <tr><th>Car Type</th><td>{car_type_label}</td></tr>
                    </table>
                </div>
                <div class="section">
                    <h3>Selected Vehicles</h3>
                    <table>
                        <thead>
                            <tr><th>Vehicle</th><th>Date/Time</th><th>Capacity</th><th>Unit Price</th></tr>
                        </thead>
                        <tbody>
                            {items_rows_html}
                        </tbody>
                    </table>
                </div>
                <div class="section">
                    <table>
                        <tr><th>Total</th><td>{total:.2f} USD</td></tr>
                    </table>
                </div>
                <p style="margin-top: 20px; color: #777;">This email was sent automatically from the booking system.</p>
            </div>
        </body>
        </html>
        """
        text_body = (
            "Booking Confirmation\n\n"
            f"Name: {guest_name}\n"
            f"Email: {guest_email}\n"
            f"Phone: {guest_phone}\n"
            f"Trip Type: {trip_type}\n"
            f"People: {people}\n"
            f"Pickup: {pickup.get('datetime','')} — {pickup.get('location_name','')}\n"
            f"Dropoff: {dropoff.get('location_name','')}\n"
            + (f"Return: {(return_trip or {}).get('datetime','')} — {(return_trip or {}).get('pickup_location_name','')} → {(return_trip or {}).get('dropoff_location_name','')}\n" if return_trip else "")
            + f"Car Type: {car_type_label}\n"
            + f"Total: {total:.2f} USD\n"
        )

        subject = "Your Booking Confirmation"
        from_email = settings.DEFAULT_FROM_EMAIL

        if test_recipients:
            recipient_list = ['cmelendezgp@gmail.com', 'adolfomariscalh@hotmail.com']
        else:
            if not guest_email:
                print("ERROR: Guest email not found in order JSON for booking email.")
                return
            recipient_list = [guest_email]

        msg = EmailMultiAlternatives(subject, text_body, from_email, recipient_list)
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        print(f"Booking email sent to {recipient_list}")

    except Exception as e:
        print(f"Error sending booking email: {e}")
        import traceback
        traceback.print_exc()