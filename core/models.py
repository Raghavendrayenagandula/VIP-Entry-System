import uuid
import qrcode
from io import BytesIO
from django.db import models
from django.core.files import File
from django.utils import timezone


class VIPVisitor(models.Model):
    STATUS_CHOICES = [
        ('EXPECTED', 'Expected'),
        ('ENTERED', 'Entered'),
        ('EXITED', 'Exited'),
    ]

    pass_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    organization = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='EXPECTED')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Generate QR Code on initial save
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new and not self.qr_code:
            qr_img = qrcode.make(str(self.pass_id))
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            file_name = f'qr_{self.pass_id}.png'
            self.qr_code.save(file_name, File(buffer), save=False)
            super().save(update_fields=['qr_code'])

    def __str__(self):
        return f"{self.full_name} ({self.get_status_display()})"


class EntryExitLog(models.Model):
    ACTION_CHOICES = [
        ('ENTRY', 'Entry'),
        ('EXIT', 'Exit'),
    ]

    visitor = models.ForeignKey(VIPVisitor, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=5, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.visitor.full_name} - {self.action} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"