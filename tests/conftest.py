import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from trackers.models import Ticker

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="password123")

@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def sample_ticker(db):
    return Ticker.objects.create(symbol="AAPL", name="Apple Inc.", is_active=True)