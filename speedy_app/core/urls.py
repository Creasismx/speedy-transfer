# -*- coding: utf-8 -*-

from django.urls import path

from .views import LandingView, ResultsView, SummaryView, contact_form_view,\
      CheckoutView, create_payment, execute_payment, payment_failed, create_checkout_session, payment_success

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
    #path('paypal/create/', PaypalPaymentView.as_view(), name='ordercreate'),
    #path('paypal/validate/', PaypalValidatePaymentView.as_view(), name='paypalvalidate'),   
]
