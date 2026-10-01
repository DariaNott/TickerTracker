from django.contrib import admin

from alerts.models import PriceAlert


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ticker', 'target_price', 'condition', 'is_triggered', 'telegram_chat_id', 'created_at')
    list_filter = ('is_triggered', 'condition', 'created_at')
    search_fields = ('user__username', 'ticker__symbol', 'telegram_chat_id')
