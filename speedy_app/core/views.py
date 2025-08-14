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
        return redirect(payment.links[1].href)  # Redirect to PayPal for payment
    else:
        return render(request, 'speedy_app/payment_failed.html')

def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        return render(request, 'speedy_app/payment_success.html')
    else:
        return render(request, 'speedy_app/payment_failed.html')

def payment_checkout(request):
    return render(request, 'speedy_app/checkout.html')

def payment_failed(request):
    return render(request, 'speedy_app/payment_failed.html')

def payment_success(request):
    return render(request, 'speedy_app/payment_success.html')

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