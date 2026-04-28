from django.db import models
from ..models import Plant

class PlantImage(models.Model):

    # Liên kết với bảng Plant.
    # related_name='images' để sau này ông gọi plant.images.all() là ra hết ảnh.
    plant = models.ForeignKey(Plant, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='plants/gallery/', verbose_name="Hình ảnh chi tiết")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ảnh chi tiết cây"
        verbose_name_plural = "Thư viện ảnh"