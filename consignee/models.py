from django.db import models
from django.conf import settings
from django.utils import timezone

class Reservasi(models.Model):
    STATUS_CHOICES = [
        (0, 'Awaiting Approval'),
        (1, 'In Progress'),
        (2, 'Cancelled by Consignee'),
        (3, 'Cancelled by Admin'),
    ]

    TRACK_IN_CHOICES = [
        (0, 'Awaiting Schedule'),
        (1, 'Scheduled'),
        (2, 'Gate In'),
        (3, 'Inspection'),
        (4, 'Washing / Cleaning'),
        (5, 'EOR Check'),
        (6, 'Repair'),
        (7, 'Stacking'),
    ]

    TRACK_OUT_CHOICES = [
        (0, 'Awaiting Confirmation'),
        (1, 'Scheduled'),
        (2, 'Gate In'),
        (3, 'Inspection'),
        (4, 'Delivery Order Processing'),
        (5, 'Gate Out'),
    ]

    reservasi_id = models.CharField(max_length=50)
    data_container = models.CharField(max_length=100)
    data_truck = models.CharField(max_length=100)
    consignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    track_in = models.IntegerField(choices=TRACK_IN_CHOICES, null=True)
    track_out = models.IntegerField(choices=TRACK_OUT_CHOICES, null=True)
    created_at = models.DateTimeField(default=timezone.now)  # Gunakan default di awal
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reservasi_id} - {self.data_container}"
