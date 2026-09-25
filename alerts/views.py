from django.shortcuts import render
from rest_framework import viewsets

from alerts.models import PriceAlert
from alerts.serializers import PriceAlertSerializer


class PriceAlertViewSet(viewsets.ModelViewSet):
    serializer_class = PriceAlertSerializer
    queryset = PriceAlert.objects.all()

    def get_queryset(self):
        return PriceAlert.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)