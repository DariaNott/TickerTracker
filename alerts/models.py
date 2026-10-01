from django.db import models
from trackers.models import Ticker
from django.contrib.auth import get_user_model

User = get_user_model()

class PriceAlert(models.Model):
    CONDITION_CHOICES = (
        ('ABOVE', 'Above'),
        ('BELOW', 'Below'),
    )
    INTERVAL_CHOICES = (
        ('1m', '1 хвилина'),
        ('1h', '1 година'),
        ('1d', '1 день'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE, related_name='alerts')
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    check_interval = models.CharField(max_length=5, choices=INTERVAL_CHOICES, default='1m')
    is_triggered = models.BooleanField(default=False)
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticker.symbol} {self.condition} {self.target_price} ({self.get_check_interval_display()})"