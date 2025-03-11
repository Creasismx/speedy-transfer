from django.db import models

class Zone(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Hotel(models.Model):
    name = models.CharField(max_length=200)
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
