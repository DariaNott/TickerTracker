from django.db import models

class PriceAlert(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    ticker = models.ForeignKey('trackers.Ticker', on_delete=models.CASCADE)
    target_price = models.DecimalField(max_digits=12, decimal_places=4)
    condition = models.CharField(max_length=5, choices=[('ABOVE', 'Above'), ('BELOW', 'Below')])
    is_triggered = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(null=True)