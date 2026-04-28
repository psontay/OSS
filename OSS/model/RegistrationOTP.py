from datetime import timedelta

from django.db import models
from django.utils import timezone


class RegistrationOTP(models.Model):
    # Dùng string 'User' hoặc settings.AUTH_USER_MODEL để tránh Circular Import
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # Mã xác thực đăng ký có thể cho lâu hơn tí, ví dụ 10 phút
        return timezone.now() < self.created_at + timedelta(minutes=10)