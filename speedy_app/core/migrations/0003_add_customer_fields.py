# Generated manually to add customer fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_car_quantity'),
    ]

    operations = [
        # Add new customer information fields
        migrations.AddField(
            model_name='booking',
            name='customer_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='customer_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='customer_address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='customer_city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='customer_zip',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='customer_country',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='customer_company',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        # Add payment information fields
        migrations.AddField(
            model_name='booking',
            name='total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='currency',
            field=models.CharField(default='USD', max_length=3),
        ),
        migrations.AddField(
            model_name='booking',
            name='payment_method',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='trip_type',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
