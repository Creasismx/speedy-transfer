from django.contrib import admin

from .models import Zone, Hotel, CarType, Car, Rate, Reservation, Payment, Booking, Contact

admin.site.register(Zone)
admin.site.register(Hotel)
admin.site.register(CarType)
admin.site.register(Car)
admin.site.register(Rate)
admin.site.register(Reservation)
admin.site.register(Payment)
admin.site.register(Booking)
admin.site.register(Contact)



