from django.db import models
from django.contrib.auth.models import User
from trackers.models import Ticker


class PriceAlert(models.Model):
    CONDITION_CHOICES = [
        ('ABOVE', 'Price is Above'),
        ('BELOW', 'Price is Below'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE, related_name='alerts')
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=5, choices=CONDITION_CHOICES)
    is_triggered = models.BooleanField(default=False)

    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True,
                                        help_text="Telegram Chat ID for notifications")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.ticker.symbol} {self.condition} {self.target_price}"