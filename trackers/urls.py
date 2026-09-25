from django.urls import path, include
from rest_framework.routers import DefaultRouter
from trackers.views import TickerViewSet

router = DefaultRouter()
router.register(r'tickers', TickerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]