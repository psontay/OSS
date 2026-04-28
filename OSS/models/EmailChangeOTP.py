from datetime import timedelta

from django.db import models
from django.utils import timezone

from OSS import settings


class EmailChangeOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    new_email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # Hiệu lực 5-10 phút tùy ông
        return timezone.now() < self.created_at + timedelta(minutes=5)
