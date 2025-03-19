# -*- coding: utf-8 -*-

from django.urls import path, include

from .views import LandingView, contact_form_view

app_name = 'core'

urlpatterns = [
    path('', LandingView.as_view(), name="home_view"),
    path('contact/', contact_form_view, name='contact-form'),
]
