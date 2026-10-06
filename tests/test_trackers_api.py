from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from trackers.models import Ticker, PriceHistory


def test_list_returns_only_active_tickers(auth_client):
    t_active = Ticker.objects.create(symbol="AAA", name="Active A", is_active=True)
    Ticker.objects.create(symbol="BBB", name="Inactive B", is_active=False)

    url = reverse("ticker-list")
    resp = auth_client.get(url)
    assert resp.status_code == 200
    symbols = [item["symbol"] for item in resp.data]
    assert t_active.symbol in symbols
    assert "BBB" not in symbols


def test_history_returns_latest_50_in_desc_order(auth_client, sample_ticker):
    start = timezone.now() - timedelta(minutes=60)
    for i in range(60):
        PriceHistory.objects.create(
            ticker=sample_ticker,
            price=Decimal("1.0000") + Decimal(i),
            timestamp=start + timedelta(minutes=i),
        )

    url = reverse("ticker-history", args=[sample_ticker.id])
    resp = auth_client.get(url)
    assert resp.status_code == 200
    data = resp.data
    assert len(data) == 50

    timestamps = [item["timestamp"] for item in data]
    assert timestamps == sorted(timestamps, reverse=True)
