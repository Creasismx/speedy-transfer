# -*- coding: utf-8 -*-

from django.urls import path

from . import views
from .views import LandingView, ResultsView, SummaryView, contact_form_view,\
    CheckoutView, create_payment, execute_payment, payment_failed, create_checkout_session, payment_success,\
    mock_stripe_checkout, mock_payment_success, twilio_whatsapp_webhook, send_whatsapp_endpoint, test_upload, test_upload

app_name = 'core'

urlpatterns = [
    path('', LandingView.as_view(), name="home_view"),
    path('search-results/', ResultsView.as_view(), name="results_view"),
    path('summary/', SummaryView.as_view(), name="summary_view"),
    path('checkout/', CheckoutView.as_view(), name="checkout_view"),
    path('contact/', contact_form_view, name='contact-form'),
    path('create_payment/', create_payment, name='create_payment'),
    path('create_checkout_session/', create_checkout_session, name='create_checkout_session'),
    path('execute_payment/', execute_payment, name='execute_payment'),
    path('payment_failed/', payment_failed, name='payment_failed'),
    path('payment_success/', payment_success, name='payment_success'),
    # Backwards-compatible aliases expected by some tests
    path('payment/failed/', payment_failed),
    path('payment/success/', payment_success),
    path('mock_stripe_checkout/', mock_stripe_checkout, name='mock_stripe_checkout'),
    path('mock_payment_success/', mock_payment_success, name='mock_payment_success'),
    # Twilio WhatsApp endpoints
    path('twilio/whatsapp/webhook/', twilio_whatsapp_webhook, name='twilio_whatsapp_webhook'),
    path('twilio/whatsapp/send/', send_whatsapp_endpoint, name='twilio_whatsapp_send'),
    path('test_upload/', views.test_upload, name='test_upload'),
    # Note: Reports URLs are handled by the dedicated 'reports' app (see config/urls.py)
    # Admin reports are available at /admin/reports/
    #path('paypal/create/', PaypalPaymentView.as_view(), name='ordercreate'),
    #path('paypal/validate/', PaypalValidatePaymentView.as_view(), name='paypalvalidate'),   
]
