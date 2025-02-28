# -*- coding: utf-8 -*-

from django.urls import path, include

from .views import LandingView

app_name = 'core'

urlpatterns = [
    path('', LandingView.as_view(), name="home_view"),
]
