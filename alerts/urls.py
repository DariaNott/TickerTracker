from django.urls import path, include
from rest_framework.routers import DefaultRouter
from alerts.views import PriceAlertViewSet

router = DefaultRouter()
router.register(r'alerts', PriceAlertViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
