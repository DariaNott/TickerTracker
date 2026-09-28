import pytest
from unittest.mock import patch
from django.urls import reverse
from alerts.models import PriceAlert

@pytest.mark.django_db
def test_get_tickers_list(auth_client, sample_ticker):
    url = reverse('ticker-list')
    response = auth_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['symbol'] == 'AAPL'

@pytest.mark.django_db
def test_create_price_alert(auth_client, sample_ticker, user):
    url = reverse('pricealert-list')
    payload = {
        "ticker": sample_ticker.id,
        "target_price": "200.00",
        "condition": "ABOVE"
    }
    response = auth_client.post(url, payload)
    assert response.status_code == 211 or response.status_code == 201
    assert PriceAlert.objects.filter(user=user, ticker=sample_ticker).exists()

@pytest.mark.django_db
@patch('trackers.tasks.yf.Ticker')
def test_check_ticker_price_task(mock_yf, sample_ticker, user):
    from alerts.models import PriceAlert
    from trackers.tasks import check_ticker_price
    from trackers.models import PriceHistory

    mock_ticker_instance = mock_yf.return_value
    mock_ticker_instance.fast_info = {'lastPrice': 250.0}

    alert = PriceAlert.objects.create(
        user=user, ticker=sample_ticker, target_price=200.0, condition="ABOVE"
    )

    check_ticker_price()

    alert.refresh_from_db()
    assert alert.is_triggered is True
    assert PriceHistory.objects.filter(ticker=sample_ticker).count() == 1