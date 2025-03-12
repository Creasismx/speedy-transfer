from django.db import models

class Zone(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)  # Optional description field
    image = models.ImageField(upload_to='zones/', blank=True, null=True)  # Optional image field

    def __str__(self):
        return self.name


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)  # Optional description field
    image = models.ImageField(upload_to='hotels/', blank=True, null=True)  # Optional image field
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name='hotels',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.name} ({self.zone})"


class Car(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)  # Optional description field
    image = models.ImageField(upload_to='cars/', blank=True, null=True)  # Optional image field
    max = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name


class Rate(models.Model):
    TRAVEL_TYPE_CHOICES = [
        ('ONE_WAY', 'One Way'),
        ('ROUND_TRIP', 'Round Trip'),
    ]

    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name='rates'
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='rates'
    )
    travel_type = models.CharField(
        max_length=10,
        choices=TRAVEL_TYPE_CHOICES
    )
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.zone} - {self.car} ({self.travel_type}): {self.price}"


# New models for reservation and payments

class Reservation(models.Model):
    """
    Represents a reservation with contact and company information.
    """
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reservation {self.id} - {self.name}"


class Payment(models.Model):
    """
    Represents a payment related to a reservation.
    """
    PAYMENT_METHOD_CHOICES = [
        ('PAYPAL', 'PayPal'),
        ('CASH_ON_ARRIVAL', 'Cash on Arrival'),
        ('STRIPE', 'Stripe'),
    ]

    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} for Reservation {self.reservation.id} via {self.get_method_display()}: {self.amount}"


# New Booking model

class Booking(models.Model):
    """
    Represents a booking with travel and client information.
    """
    client_id = models.CharField(max_length=100)
    # Relationship with Hotel model
    pickup_location1 = models.ForeignKey(
        Hotel,
        on_delete=models.SET_NULL,
        related_name='pickup_location1_bookings',
        null=True,
        blank=True
    )
    dropoff_location1 = models.ForeignKey(
        Hotel,
        on_delete=models.SET_NULL,
        related_name='dropoff_location1_bookings',
        null=True,
        blank=True
    )
    pickup_location2 = models.ForeignKey(
        Hotel,
        on_delete=models.SET_NULL,
        related_name='pickup_location2_bookings',
        null=True,
        blank=True
    )
    dropoff_location2 = models.ForeignKey(
        Hotel,
        on_delete=models.SET_NULL,
        related_name='dropoff_location2_bookings',
        null=True,
        blank=True
    )
    pickup_date_time = models.DateTimeField()
    return_date_time = models.DateTimeField()
    car_type = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    date_capture = models.DateTimeField(auto_now_add=True)
    how_people = models.PositiveIntegerField(default=1)
    one_way = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking {self.id} for Client {self.client_id}"
