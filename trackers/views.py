from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from trackers.models import Ticker, PriceHistory
from trackers.serializers import TickerSerializer, PriceHistorySerializer


class TickerViewSet(viewsets.ModelViewSet):
    queryset = Ticker.objects.all()
    serializer_class = TickerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ticker.objects.filter(is_active=True)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        GET /api/v1/tickers/{id}/history/
        returns a list of price history records for a specific ticker.
        """
        ticker = self.get_object()
        history_records = PriceHistory.objects.filter(ticker=ticker).order_by('-timestamp')[:50]  # Останні 50 записів

        serializer = PriceHistorySerializer(history_records, many=True)
        return Response(serializer.data)
