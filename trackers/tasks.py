from celery import shared_task
import yfinance as yf
from alerts.models import PriceAlert
from trackers.models import Ticker, PriceHistory
from django.utils import timezone
from decimal import Decimal
import logging
from alerts.services import send_telegram_notification

logger = logging.getLogger(__name__)

@shared_task
def check_ticker_price():
    tickers = Ticker.objects.filter(is_active=True)

    for ticker in tickers:
        try:
            data = yf.Ticker(ticker.symbol)
            raw_price = data.fast_info.get('lastPrice')

            if raw_price is None:
                price = None
                continue
            else:
                price = Decimal(str(round(raw_price, 4)))

            PriceHistory.objects.create(ticker=ticker, price=price)

            alerts = PriceAlert.objects.filter(ticker=ticker, is_triggered=False)

            for alert in alerts:
                condition_met = (
                    (alert.condition == 'ABOVE' and price >= alert.target_price) or
                    (alert.condition == 'BELOW' and price <= alert.target_price)
                )

                if condition_met:
                    alert.is_triggered = True
                    alert.save()

                    if alert.telegram_chat_id:
                        msg = (
                            f"🚨 <b>Ціна змінилася!</b>\n\n"
                            f"📈 Тікер: <b>{ticker.symbol}</b>\n"
                            f"💵 Поточна ціна: <b>${price:.2f}</b>\n"
                            f"🎯 Цільова ціна: <b>${alert.target_price:.2f}</b> ({alert.condition})"
                        )
                        send_telegram_notification(alert.telegram_chat_id, msg)

        except Exception as e:
            print(f"Error processing {ticker.symbol}: {e}")