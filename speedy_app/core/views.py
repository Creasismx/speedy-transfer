from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Zone

class LandingView(TemplateView):
    template_name = "speedy_app/landing_page.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['zones'] = Zone.objects.all()
        return context