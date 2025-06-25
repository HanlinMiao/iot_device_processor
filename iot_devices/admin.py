from django.contrib import admin
from .models import Device, Payload

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['devEUI', 'name', 'latest_status', 'created_at', 'updated_at']
    list_filter = ['latest_status', 'created_at']
    search_fields = ['devEUI', 'name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Payload)
class PayloadAdmin(admin.ModelAdmin):
    list_display = ['device', 'fCnt', 'status', 'data_hex', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['device__devEUI', 'fCnt']
    readonly_fields = ['created_at', 'data_hex']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('device')
