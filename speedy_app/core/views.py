import paypalrestsdk
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import HttpResponse
from .models import Zone, Contact, Car
#from .utils import make_paypal_payment, verify_paypal_payment
#import paypalrestsdk
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
import stripe  # new

#For sending mail uppong form submission
from django.core.mail import send_mail


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
        context['zones'] = Zone.objects.all()
        context['cars'] = Car.objects.all()
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
        context['pickup_datetime'] = query.get('pickup_datetime', '')
        context['pickup_location'] = query.get('pickup_location', '')
        context['dropoff_location'] = query.get('dropoff_location', '')
        context['return_datetime'] = query.get('return_datetime', '')
        context['people'] = query.get('people', '')
        context['car_type'] = query.get('car_type', '')
        context['trip_type'] = query.get('trip_type', 'oneway')

        # Optionally, filter or process results based on these parameters here

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
    Saves the form data to the database and sends an email.
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
        email_body = f"""
        New Contact Form Submission from the website:

        Name: {name}
        Email: {email}
        Phone: {phone}
        Country: {country}
        Company: {company}
        Interested in: {interested_in}
        Message: {message}
        """
        
        try:
            send_mail(
                subject='New Contact Form Submission',
                message=email_body,
                # This line has been updated to use the DEFAULT_FROM_EMAIL from settings.py
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['cmelendezgp@gmail.com'], # The recipient email
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending contact email: {e}")
            # The database save was successful, so we'll still show a success message
            # but you might want to log this error for your own records.
        
        messages.success(request, "Your message has been submitted successfully!")
        
        # This line has been updated to use the correct URL name from your urls.py
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

