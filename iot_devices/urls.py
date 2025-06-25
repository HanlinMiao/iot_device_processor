from django.urls import path

from .views import (
    PayloadCreateView,
    DeviceListView,
    DeviceDetailView,
    PayloadListView
)

urlpatterns = [
    path('payloads/', PayloadCreateView.as_view(), name='payload-create'),
    path('payloads/list/', PayloadListView.as_view(), name='payload-list'),
    path('devices/', DeviceListView.as_view(), name='device-list'),
    path('devices/<str:devEUI>/', DeviceDetailView.as_view(), name='device-detail'),
]
