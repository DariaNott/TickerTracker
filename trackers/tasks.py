from celery import shared_task
import yfinance as yf
from alerts.models import PriceAlert
from trackers.models import Ticker, PriceHistory
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


@shared_task()
def check_ticker_price():
    active_tickers = Ticker.objects.filter(is_active=True)
    if not active_tickers:
        return None
    for ticker in active_tickers:
        try:
            raw_price = yf.Ticker(ticker.symbol).fast_info['lastPrice']
            price = Decimal(str(round(raw_price, 4)))
        except Exception as e:
            print(f"Error occurred while fetching price for {ticker.symbol}: {e}")
            continue
        PriceHistory.objects.create(ticker=ticker, price=price)
        alerts = PriceAlert.objects.filter(ticker=ticker, is_triggered=False)
        if alerts:
            for alert in alerts:
                if alert.condition == 'ABOVE' and price >= alert.target_price:
                    alert.is_triggered = True
                    alert.triggered_at = timezone.now()
                    alert.save()
                elif alert.condition == 'BELOW' and price <= alert.target_price:
                    alert.is_triggered = True
                    alert.triggered_at = timezone.now()
                    alert.save()
