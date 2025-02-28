from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.

class LandingView(TemplateView):
    template_name = "speedy_app/landing_page.html"