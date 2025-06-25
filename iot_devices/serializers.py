from rest_framework import serializers
from .models import Device, Payload
import base64

class PayloadSerializer(serializers.ModelSerializer):
    # Include all the IoT payload fields
    devEUI = serializers.CharField(write_only=True)  # Only for input, not output
    device_devEUI = serializers.CharField(source='device.devEUI', read_only=True)  # For output
    fCnt = serializers.IntegerField()
    data = serializers.CharField()
    rxInfo = serializers.ListField(required=False, allow_empty=True, write_only=True)
    txInfo = serializers.DictField(required=False, write_only=True)

    class Meta:
        model = Payload
        fields = ['id', 'devEUI', 'device_devEUI', 'fCnt', 'data', 'rxInfo', 'txInfo', 'data_hex', 'status', 'raw_payload', 'created_at']
        read_only_fields = ['id', 'device_devEUI', 'data_hex', 'status', 'raw_payload', 'created_at']

    def validate(self, attrs):
        # Check for duplicate fCnt for the same device
        devEUI = attrs.get('devEUI')
        fCnt = attrs.get('fCnt')

        try:
            device = Device.objects.get(devEUI=devEUI)
            if Payload.objects.filter(device=device, fCnt=fCnt).exists():
                raise serializers.ValidationError(
                    f"Duplicate payload: fCnt {fCnt} already exists for device {devEUI}"
                )
        except Device.DoesNotExist:
            # Device will be created, so no duplicate check needed
            pass

        return attrs

    def validate_data(self, value):
        """Validate that data is proper base64"""
        try:
            base64.b64decode(value)
        except Exception:
            raise serializers.ValidationError("Invalid base64 data")
        return value

    def create(self, validated_data):
        # Extract the non-model fields
        devEUI = validated_data.pop('devEUI')
        rxInfo = validated_data.pop('rxInfo', [])
        txInfo = validated_data.pop('txInfo', {})

        # Store original payload for reference
        raw_payload = {
            'devEUI': devEUI,
            'fCnt': validated_data['fCnt'],
            'data': validated_data['data'],
            'rxInfo': rxInfo,
            'txInfo': txInfo
        }

        # Get or create device
        device, created = Device.objects.get_or_create(
            devEUI=devEUI,
            defaults={'name': f'Device {devEUI}'}
        )

        # Decode base64 to hex
        data_b64 = validated_data['data']
        try:
            decoded_data = base64.b64decode(data_b64)
            data_hex = decoded_data.hex().upper()
        except Exception as e:
            raise serializers.ValidationError(f"Error decoding base64 data: {str(e)}")

        # Determine status based on hex value
        # If hex represents the value 1, then passing, otherwise failing
        try:
            # Convert hex to integer to check if it equals 1
            data_int = int(data_hex, 16)
            status = 'passing' if data_int == 1 else 'failing'
        except ValueError:
            status = 'failing'  # If conversion fails, mark as failing

        # Create payload with processed data
        payload = Payload.objects.create(
            device=device,
            fCnt=validated_data['fCnt'],
            data=validated_data['data'],
            data_hex=data_hex,
            status=status,
            raw_payload=raw_payload
        )

        # Update device's latest status
        device.latest_status = status
        device.save()

        return payload


class DeviceSerializer(serializers.ModelSerializer):
    payloads_count = serializers.SerializerMethodField()
    latest_payload = serializers.SerializerMethodField()
    latest_gateway_info = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = ['id', 'devEUI', 'name', 'description', 'latest_status',
                 'payloads_count', 'latest_payload', 'latest_gateway_info', 'created_at', 'updated_at']

    def get_payloads_count(self, obj):
        return obj.payloads.count()

    def get_latest_payload(self, obj):
        latest = obj.payloads.first()
        if latest:
            return {
                'id': latest.id,
                'fCnt': latest.fCnt,
                'status': latest.status,
                'data_hex': latest.data_hex,
                'created_at': latest.created_at
            }
        return None
