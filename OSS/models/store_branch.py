from django.contrib.gis.db import models

class StoreBranch(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên chi nhánh")
    address = models.CharField(max_length=500, verbose_name="Địa chỉ")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    
    location = models.PointField(srid=4326, verbose_name="Vị trí tọa độ", blank=True, null=True)

    delivery_radius = models.IntegerField(default=5000, help_text="Đơn vị: mét", verbose_name="Bán kính giao hàng")

    image = models.ImageField(upload_to='branch_images/', blank=True, null=True, verbose_name="Ảnh cửa hàng")
    
    opening_hours = models.CharField(max_length=100, blank=True, verbose_name="Giờ mở cửa")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chi nhánh cửa hàng"
        verbose_name_plural = "Các chi nhánh cửa hàng"
    def __str__(self):
        return self.name