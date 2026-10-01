from rest_framework import serializers
from .models import PriceAlert

class PriceAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceAlert
        fields = ['id', 'user', 'ticker', 'target_price', 'condition', 'is_triggered', 'telegram_chat_id', 'created_at']
        read_only_fields = ['user', 'is_triggered', 'created_at']