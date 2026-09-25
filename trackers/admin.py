from django.contrib import admin

from trackers.models import PriceHistory, Ticker


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'price', 'timestamp')

@admin.register(Ticker)
class TickerAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'is_active', 'created_at')