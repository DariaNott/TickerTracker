from .models import PriceAlert
from rest_framework import serializers

class PriceAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceAlert
        fields = ['user', 'ticker', 'target_price', 'condition', 'is_triggered', 'triggered_at']
        read_only_fields = ['user', 'is_triggered', 'created_at']