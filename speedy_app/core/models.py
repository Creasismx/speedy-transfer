from django.db import models

class Zone(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)  # Optional description field
    image = models.ImageField(upload_to='zones/', blank=True, null=True)  # Optional image field

    def __str__(self):
        return self.name


class CarType(models.Model):
    """
    Catalog of car types for consistent categorization.
    """
    code = models.CharField(max_length=10, unique=True)  # e.g., 'SEDAN', 'SUV'
    name = models.CharField(max_length=50)  # e.g., 'Sedan', 'SUV'
    description = models.TextField(blank=True, null=True)
    max_capacity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    class Meta:
        verbose_name_plural = "Car Types"


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
    car_type = models.ForeignKey(
        CarType,
        on_delete=models.CASCADE,
        related_name='cars',
        null=False,  # NOT NULL - cada carro debe tener un tipo
        blank=False
    )
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='cars/', blank=True, null=True)
    max = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.name} ({self.car_type.name})"

    class Meta:
        verbose_name_plural = "Cars"


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
    # Customer Information
    client_id = models.CharField(max_length=100)  # Email as unique identifier
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    customer_first_name = models.CharField(max_length=100, blank=True, null=True)
    customer_last_name = models.CharField(max_length=100, blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    flight_number = models.CharField(max_length=50, blank=True, null=True)
    customer_address = models.TextField(blank=True, null=True)
    customer_city = models.CharField(max_length=100, blank=True, null=True)
    customer_zip = models.CharField(max_length=20, blank=True, null=True)
    customer_state = models.CharField(max_length=100, blank=True, null=True)
    customer_country = models.CharField(max_length=100, blank=True, null=True)
    customer_company = models.CharField(max_length=200, blank=True, null=True)
    customer_date_of_birth = models.DateField(blank=True, null=True)
    customer_passport_number = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)
    
    # Trip Information
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
    car_id = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='bookings',
        db_column='car_id'
    )
    date_capture = models.DateTimeField(auto_now_add=True)
    how_people = models.PositiveIntegerField(default=1)
    one_way = models.BooleanField(default=False)
    
    # Payment Information
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, default='USD')
    payment_method = models.CharField(max_length=20, blank=True, null=True)
    trip_type = models.CharField(max_length=20, blank=True, null=True)  # oneway/roundtrip

    def __str__(self):
        return f"Booking {self.id} for Client {self.client_id}"
    
class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    interested_in = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    # New fields for Version 2
    whatsapp_number = models.CharField(max_length=32, blank=True, null=True)
    preferred_contact_method = models.CharField(max_length=20, blank=True, null=True, choices=[('email','Email'),('phone','Phone'),('whatsapp','WhatsApp')])
    subscribe_newsletter = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.email}"


class WhatsAppConversation(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='whatsapp_conversations')
    started_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"WhatsAppConversation {self.id} for {self.contact.email}"


class WhatsAppMessage(models.Model):
    conversation = models.ForeignKey(WhatsAppConversation, on_delete=models.CASCADE, related_name='messages')
    sent_at = models.DateTimeField(auto_now_add=True)
    sender = models.CharField(max_length=50, choices=[('user','User'),('agent','Agent')])
    content = models.TextField()
    direction = models.CharField(max_length=10, choices=[('inbound','Inbound'),('outbound','Outbound')])

    def __str__(self):
        return f"Msg {self.id} ({self.direction}) @ {self.sent_at}"


class Certificate(models.Model):
    """
    Model for managing certificates and trust badges displayed on the home page.
    """
    CERTIFICATE_TYPE_CHOICES = [
        ('certificate', 'Certificate'),
        ('trust_badge', 'Trust Badge'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200, blank=True, null=True)
    certificate_type = models.CharField(max_length=20, choices=CERTIFICATE_TYPE_CHOICES, default='certificate')
    icon_svg = models.TextField(help_text="SVG path element (the 'd' attribute value)")
    icon_color = models.CharField(max_length=7, default='#4abbc1', help_text="Hex color code for icon background")
    display_order = models.PositiveIntegerField(default=0, help_text="Order in which certificates are displayed")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'created_at']
        verbose_name = "Certificate"
        verbose_name_plural = "Certificates"
    
    def __str__(self):
        return f"{self.title} ({self.get_certificate_type_display()})"

