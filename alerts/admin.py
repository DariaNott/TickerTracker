from django.contrib import admin

from alerts.models import PriceAlert


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticker', 'target_price', 'condition', 'is_triggered', 'triggered_at')