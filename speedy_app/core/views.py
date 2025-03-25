from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import HttpResponse
from .models import Zone, Contact, Car

class LandingView(TemplateView):
    template_name = "speedy_app/landing_page.html"
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