from django.db import models

class Device(models.Model):
    STATUS_CHOICES = [
        ('passing', 'Passing'),
        ('failing', 'Failing'),
    ]

    devEUI = models.CharField(max_length=100, unique=True, help_text="Device EUI identifier")
    name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    latest_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='failing',
        help_text="Latest status based on most recent payload"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Device {self.devEUI} - {self.latest_status}"

    class Meta:
        ordering = ['-updated_at']

class Payload(models.Model):
    STATUS_CHOICES = [
        ('passing', 'Passing'),
        ('failing', 'Failing'),
    ]

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='payloads',
        help_text="Device this payload belongs to"
    )
    fCnt = models.BigIntegerField(help_text="Frame counter for duplicate detection")
    data = models.TextField(help_text="Base64 encoded data")
    data_hex = models.CharField(max_length=500, help_text="Hexadecimal representation of data")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        help_text="Status determined from data value"
    )
    raw_payload = models.JSONField(help_text="Original payload received")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payload {self.fCnt} for {self.device.devEUI} - {self.status}"

    class Meta:
        ordering = ['-created_at']
        unique_together = ['device', 'fCnt']  # Prevent duplicate fCnt for same device
