from django.contrib.gis.db import models as gis_models
from django.db import models
from django.conf import settings
from .plant import Plant

class Order(models.Model):
    # Dùng chữ HOA cho chuẩn Django, nhưng lưu ý trong HTML ông cũng phải check đúng chữ HOA
    STATUS_CHOICES = [
        ('PENDING', 'Chờ xử lý'),
        ('CONFIRMED', 'Đã xác nhận'),
        ('SHIPPING', 'Đang giao hàng'),
        ('COMPLETED', 'Đã hoàn thành'),
        ('CANCELLED', 'Đã hủy'),
    ]

    # Liên kết với User
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Khách hàng",
        null=True,
        blank=True
    )

    # Thông tin người nhận (Lưu cứng tại thời điểm mua)
    full_name = models.CharField(max_length=200, verbose_name="Người nhận")
    email = models.EmailField()
    phone = models.CharField(max_length=15, verbose_name="Số điện thoại")
    address = models.TextField(verbose_name="Địa chỉ chi tiết")

    # GIS: Tọa độ giao hàng (Để tính phí ship sau này)
    delivery_location = gis_models.PointField(srid=4326, null=True, blank=True)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="Phí giao hàng")

    total_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Tổng tiền")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Danh sách đơn hàng"

    def __str__(self):
        return f"Đơn hàng #{self.id} - {self.full_name}"


class OrderItem(models.Model):
    # related_name='items' RẤT QUAN TRỌNG để chạy logic hoàn kho của mình
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    plant = models.ForeignKey(Plant, on_delete=models.PROTECT, verbose_name="Cây cảnh")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Giá lúc mua")

    def __str__(self):
        return f"{self.plant.name} (x{self.quantity})"

    @property
    def get_subtotal(self):
        return self.price * self.quantity