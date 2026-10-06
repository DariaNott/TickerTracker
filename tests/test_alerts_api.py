from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal

from alerts.models import PriceAlert


def test_create_price_alert_sets_user_ignoring_payload_user(auth_client, sample_ticker, user):
    User = get_user_model()
    other_user = User.objects.create_user(username="u2", password="pass2")

    url = reverse("pricealert-list")
    payload = {
        "ticker": sample_ticker.id,
        "target_price": "123.45",
        "condition": "ABOVE",
        "user": other_user.id,
    }
    resp = auth_client.post(url, payload, format="json")
    assert resp.status_code == 201

    data = resp.data
    assert data["user"] == user.id
    assert PriceAlert.objects.filter(
        id=data["id"],
        user=user,
        ticker=sample_ticker,
        condition="ABOVE",
        target_price=Decimal("123.45"),
    ).exists()


def test_list_returns_only_current_user_alerts(auth_client, sample_ticker, user):
    User = get_user_model()
    other_user = User.objects.create_user(username="uX", password="passX")

    PriceAlert.objects.create(
        user=user, ticker=sample_ticker, target_price=Decimal("10.00"), condition="ABOVE"
    )
    PriceAlert.objects.create(
        user=other_user, ticker=sample_ticker, target_price=Decimal("20.00"), condition="BELOW"
    )

    url = reverse("pricealert-list")
    resp = auth_client.get(url)
    assert resp.status_code == 200
    data = resp.data

    assert len(data) == 1
    assert data[0]["user"] == user.id
