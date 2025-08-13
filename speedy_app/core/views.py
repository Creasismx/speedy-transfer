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

        # NEW LOGIC: Expand vehicles based on quantity to create individual vehicle options
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

                # Generate individual vehicle options based on quantity field PER CAR in each rate
                for rate in rates:
                    car = rate.car
                    vehicle_quantity = car.quantity if getattr(car, 'quantity', None) else 1

                    # Resolve image URL: prefer MEDIA file URL; if not available, fall back to static assets path
                    image_url = None
                    try:
                        if car.image and hasattr(car.image, 'url'):
                            image_url = car.image.url
                    except Exception:
                        image_url = None

                    if not image_url:
                        # Try to use the raw value if provided as a URL or filename
                        raw_value = None
                        try:
                            raw_value = car.image.name if car.image else None
                        except Exception:
                            raw_value = None
                        if raw_value:
                            raw_value = raw_value.strip()
                            # Absolute URL provided directly
                            if raw_value.lower().startswith(("http://", "https://", "//")):
                                image_url = raw_value
                            else:
                                # Ensure there is an extension, default to .jpg
                                basename = os.path.basename(raw_value)
                                if "." not in basename:
                                    basename = f"{basename}.jpg"
                                # URL-encode to handle spaces and special chars like '#'
                                image_url = static(f"images/cars/{quote(basename)}")

                    # Fallback to a default per car type
                    if not image_url:
                        default_per_type = {
                            'VAN': 'Van_Dark.jpg',
                            'SPRINTER': 'Small_Sprinter.jpg',
                        }
                        default_name = default_per_type.get(car.type)
                        if default_name:
                            image_url = static(f"images/cars/{quote(default_name)}")
                    
                    print(f"Processing rate {rate.id}: Car={car.name} (type={car.type}), Quantity={vehicle_quantity}, Price=${rate.price}")
                    
                    # Create individual vehicle options based on quantity
                    for unit_number in range(1, vehicle_quantity + 1):
                        # Create unique identifier for each unit
                        unique_id = f"{rate.id}_{unit_number}" if vehicle_quantity > 1 else str(rate.id)
                        
                        # Format vehicle name based on quantity
                        vehicle_name = f"{car.name} #{unit_number:03d}" if vehicle_quantity > 1 else car.name
                        
                        transfer_options.append({
                            'id': unique_id,
                            'rate_id': rate.id,
                            'car_id': car.id,
                            'unit_number': unit_number,
                            'car_name': vehicle_name,
                            'car_description': car.description,
                            'car_capacity': car.max,
                            'image_url': image_url,
                            'price': rate.price,
                            'travel_type': rate.travel_type,
                            'departure_date': context['pickup_datetime'].split('T')[0] if context['pickup_datetime'] else '',
                            'departure_time': context['pickup_datetime'].split('T')[1] if context['pickup_datetime'] else '',
                            'availability_status': 'available',
                            'total_fleet_size': vehicle_quantity,
                            'is_fleet_vehicle': vehicle_quantity > 1
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
                            <th>Interested in:</th>
                            <td>{interested_in}</td>
                        </tr>
                    </table>

                    <p><strong>Message:</strong></p>
                    <p>{message}</p>
                    
                    <div class="footer">
                        <p>This is an automated message. Please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create a plain text version as a fallback for email clients that don't support HTML
            text_body = f"""
            New Contact Form Submission from the website:

            Name: {name}
            Email: {email}
            Phone: {phone}
            Country: {country}
            Company: {company}
            Interested in: {interested_in}
            Message: {message}
            """
            
            subject = 'New Contact Form Submission'
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
                    "total": "10.00",  # Total amount in USD
                    "currency": "USD",
                },
                "description": "Payment for Product/Service",
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

from django.shortcuts import redirect

def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': 2000,
                            'product_data': {
                                'name': 'T-shirt',
                                'description': 'Comfortable cotton t-shirt'
                            }
                        },
                        'quantity': 1
                    }
                ]
            )
            return redirect(checkout_session.url)  # ✅ Redirect to Stripe Checkout
        except Exception as e:
            return JsonResponse({'error': str(e)})