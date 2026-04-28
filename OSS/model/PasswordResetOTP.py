import random
import string
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.conf import settings # Import settings để lấy AUTH_USER_MODEL

class PasswordResetOTP(models.Model):
    # Dùng settings.AUTH_USER_MODEL là cách "thượng đẳng" nhất
    # Nó sẽ tự tìm đến Model User mà ông khai báo trong settings.py
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # Mã có hiệu lực trong 5 phút
        return not self.is_used and timezone.now() < self.created_at + timedelta(minutes=5)

    def __str__(self):
        # Lưu ý: Vì mình dùng AUTH_USER_MODEL nên đôi khi truy cập trực tiếp .email
        # cần đảm bảo User đó có trường email (Model của ông có rồi nên OK)
        return f"OTP for {self.user.email}: {self.otp_code}"