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

#paypalrestsdk.configure({
#    "mode": "sandbox",  # Change to "live" for production
#    "client_id": settings.PAYPAL_CLIENT_ID,
#    "client_secret": settings.PAYPAL_SECRET,
#})


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
        context['zones'] = Zone.objects.all()
        context['cars'] = Car.objects.all()
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

def contact_form_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        country = request.POST.get("country")
        company = request.POST.get("company")
        interested_in = request.POST.get("interested")
        message = request.POST.get("additional")

        # Save to database
        Contact.objects.create(
            name=name,
            email=email,
            phone=phone,
            country=country,
            company=company,
            interested_in=interested_in,
            message=message,
        )

        messages.success(request, "Your message has been submitted successfully!")

        return redirect("/")  # Redirects back to the form page

    return HttpResponse("Invalid request", status=400)


#class PaypalPaymentView(APIView):
#    """
#    Endpoint to create a PayPal payment and return the approval URL
#    """
#    permission_classes = [permissions.IsAuthenticated]

#    def post(self, request, *args, **kwargs):
#        amount = 20  # For example: $20
#        currency = "USD"

        # Create PayPal payment
#        status, payment_id, approved_url = make_paypal_payment(
#            amount=amount,
#            currency=currency,
#            return_url=PAYPAL_RETURN_URL,
#            cancel_url=PAYPAL_CANCEL_URL
#        )#

#        if status:
#            # Optionally: save payment_id or log it here
#            return Response({
#                "success": True,
#                "msg": "Payment link created successfully",
#                "approved_url": approved_url
#            }, status=201)
#        else:
#            return Response({
#                "success": False,
#                "msg": "Failed to create payment"
#            }, status=400)


#class PaypalValidatePaymentView(APIView):
#    """
#    Endpoint to validate if the PayPal payment was approved
#    """
#    permission_classes = [permissions.IsAuthenticated]

#    def post(self, request, *args, **kwargs):
#        payment_id = request.data.get("payment_id")

#        if not payment_id:
#            return Response({
#                "success": False,
#                "msg": "Missing payment_id"
#            }, status=400)

#        payment_status = verify_paypal_payment(payment_id=payment_id)

#        if payment_status:
#            return Response({
#                "success": True,
#                "msg": "Payment approved"
#            }, status=200)
#        else:
#            return Response({
#                "success": False,
#                "msg": "Payment failed or was cancelled"
#            }, status=200)
