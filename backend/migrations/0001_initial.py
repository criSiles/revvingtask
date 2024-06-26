# Generated by Django 5.0.6 on 2024-06-08 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RawData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('invoice_number', models.CharField(max_length=100)),
                ('value', models.DecimalField(decimal_places=2, max_digits=15)),
                ('haircut_percent', models.DecimalField(decimal_places=2, max_digits=5)),
                ('daily_fee_percent', models.DecimalField(decimal_places=3, max_digits=5)),
                ('currency', models.CharField(max_length=10)),
                ('revenue_source', models.CharField(max_length=100)),
                ('customer', models.CharField(max_length=100)),
                ('expected_payment_duration', models.IntegerField()),
            ],
        ),
    ]
