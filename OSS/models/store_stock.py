from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum

from .plant import Plant
from .store_branch import StoreBranch


class StoreStock(models.Model):
    branch = models.ForeignKey(StoreBranch, on_delete=models.CASCADE, related_name='stocks', verbose_name="Chi nhánh")

    plant = models.ForeignKey('Plant', on_delete=models.CASCADE, related_name='storestock' )
    quantity = models.PositiveIntegerField(default=0, verbose_name="Số lượng tồn kho")

    last_updated = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    class Meta:
        unique_together = ('branch', 'plant')
        verbose_name = "Kho hàng chi nhánh"
        verbose_name_plural = "Quản lý kho hàng"

    def __str__(self):
        return f"{self.branch.name} - {self.plant.name} ({self.quantity})"
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)