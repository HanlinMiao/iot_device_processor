from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from .models import Device, Payload
from .serializers import DeviceSerializer, PayloadSerializer

class PayloadCreateView(generics.CreateAPIView):
    """
    Create a new payload from IoT device

    Expected payload format:
    {
        "devEUI": "device_identifier",
        "fCnt": 12345,
        "data": "base64_encoded_data",
        "raw_payload": {...}  # optional, stores original payload
    }
    """
    serializer_class = PayloadSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {"error": "Duplicate payload detected"},
                status=status.HTTP_409_CONFLICT
            )

class DeviceListView(generics.ListAPIView):
    """List all devices with their current status"""
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

class DeviceDetailView(generics.RetrieveAPIView):
    """Get details of a specific device"""
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    lookup_field = 'devEUI'
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

class PayloadListView(generics.ListAPIView):
    """List payloads, optionally filtered by device"""
    serializer_class = PayloadSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Payload.objects.all()
        devEUI = self.request.query_params.get('devEUI', None)
        if devEUI:
            queryset = queryset.filter(device__devEUI=devEUI)
        return queryset
