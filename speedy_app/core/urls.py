# -*- coding: utf-8 -*-

from django.urls import path

from .views import LandingView, ResultsView, contact_form_view

app_name = 'core'

urlpatterns = [
    path('', LandingView.as_view(), name="home_view"),
    path('search-results/', ResultsView.as_view(), name="results_view"),
    path('contact/', contact_form_view, name='contact-form'),
]
