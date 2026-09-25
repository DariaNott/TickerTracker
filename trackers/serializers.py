from .models import Ticker, PriceHistory
from rest_framework import serializers

class TickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticker
        fields = ['id', 'symbol', 'name', 'is_active']

class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['price', 'timestamp']