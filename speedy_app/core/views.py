# First, you need to import the Hotel and Car models at the top of your file
from .models import Zone, Contact, Car, Hotel, Rate # Added Rate for the price lookup

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
        # The 'related_name' in your Hotel model is 'hotels', so we must use that here.
        context['zones_with_hotels'] = Zone.objects.prefetch_related('hotels').all()
        context['cars'] = Car.objects.all()
        # Add a placeholder for a variable that will eventually hold the form data
        context['pickup_datetime'] = ""
        context['pickup_location'] = ""
        context['people'] = ""
        context['car_type'] = ""
        context['trip_type'] = "oneway"
        return context

class ResultsView(TemplateView):
    template_name = "speedy_app/results_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Always include zones and cars (for dropdowns)
        context['zones'] = Zone.objects.all()
        context['cars'] = Car.objects.all()

        # Extract GET parameters (submitted form data)
        query = self.request.GET
        pickup_location_id = query.get('pickup_location', '')
        car_type_id = query.get('car_type', '')
        context['pickup_datetime'] = query.get('pickup_datetime', '')
        context['dropoff_location'] = query.get('dropoff_location', '')
        context['return_datetime'] = query.get('return_datetime', '')
        context['people'] = query.get('people', '')
        context['car_type'] = car_type_id
        
        # Get trip_type from the form and convert it to the database format
        trip_type_form = query.get('trip_type', 'oneway')
        if trip_type_form == 'oneway':
            travel_type_db = 'ONE_WAY'
        elif trip_type_form == 'roundtrip':
            travel_type_db = 'ROUND_TRIP'
        else:
            travel_type_db = 'ONE_WAY' # Fallback to ONE_WAY if an unexpected value is received
        
        context['trip_type'] = trip_type_form # Keep the original form value for context

        # New logic to filter and prepare transfer options
        transfer_options = []
        if pickup_location_id and car_type_id:
            try:
                # Get the hotel to find its zone_id
                pickup_hotel = Hotel.objects.get(id=pickup_location_id)
                zone_id = pickup_hotel.zone_id

                # Filter Rate based on car_id, zone_id, and the dynamically determined travel_type
                rates = Rate.objects.filter(
                    car_id=car_type_id,
                    zone_id=zone_id,
                    travel_type=travel_type_db # Now uses the dynamic value
                )

                # Get the car details for display
                car = Car.objects.get(id=car_type_id)

                # Prepare the data to pass to the template
                for rate in rates:
                    transfer_options.append({
                        'car_name': car.name,
                        'car_description': car.description,
                        'car_capacity': car.max,
                        'price': rate.price,
                        'travel_type': rate.travel_type,
                        'departure_date': context['pickup_datetime'].split('T')[0] if context['pickup_datetime'] else '',
                        'departure_time': context['pickup_datetime'].split('T')[1] if context['pickup_datetime'] else ''
                    })

            except Hotel.DoesNotExist:
                print(f"Error: Hotel with ID {pickup_location_id} not found.")
            except Car.DoesNotExist:
                print(f"Error: Car with ID {car_type_id} not found.")
            except Rate.DoesNotExist:
                print(f"Error: No rate found for car_id {car_type_id} and zone_id {zone_id} with travel type {travel_type_db}.")
        
        context['transfer_options'] = transfer_options
        
        return context

class SummaryView(TemplateView):
    template_name = "speedy_app/summary_page.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['zones'] = Zone.objects.all()
        context['cars'] = Car.objects.all()
        return context     

class CheckoutView(TemplateView):
    template_name = "speedy_app/checkout_page.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['zones'] = Zone.objects.all()
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
