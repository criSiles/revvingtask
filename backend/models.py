from django.db import models

class RawData(models.Model):
    date = models.DateField()
    invoice_number = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    haircut_percent = models.DecimalField(max_digits=5, decimal_places=2)
    daily_fee_percent = models.DecimalField(max_digits=5, decimal_places=3)
    currency = models.CharField(max_length=10)
    revenue_source = models.CharField(max_length=100)
    customer = models.CharField(max_length=100)
    expected_payment_duration = models.IntegerField()

    def __str__(self):
        return f"{self.customer} - {self.date} - {self.value}"
