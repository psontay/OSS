from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum

from .category import Category

class SoilRegion(models.Model):
    name = models.CharField(max_length=100)
    ph_level = models.FloatField()
    geom = models.PolygonField(srid=4326) 

    def __str__(self):
        return self.name

class Plant(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name="Tên cây")
    price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Giá bán")
    description = models.TextField(blank=True, null=True)
    location = models.PointField(srid=4326, verbose_name="Vườn ươm", null=True, blank=True)
    image = models.ImageField(upload_to='plants/', null=True, blank=True, verbose_name="Hình ảnh")
    # stock_quantity = models.IntegerField(default=10)
    is_available = models.BooleanField(default=True)
    
    min_temp = models.FloatField(default=20.0, verbose_name="Nhiệt độ Min (°C)")
    max_temp = models.FloatField(default=35.0, verbose_name="Nhiệt độ Max (°C)")
    
    min_ph = models.FloatField(default=5.5, verbose_name="pH Min")
    max_ph = models.FloatField(default=7.5, verbose_name="pH Max")
    
    max_clay = models.FloatField(default=60.0, verbose_name="Tỷ lệ Sét tối đa (%)")

    min_humidity = models.FloatField(default=40.0, verbose_name="Độ ẩm Min (%)")
    max_humidity = models.FloatField(default=100.0, verbose_name="Độ ẩm Max (%)")

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='plants', blank=True, null=True)

    class Meta:
        ordering = ['-id']
        verbose_name = "Cây cảnh"

    def __str__(self):
        return self.name

    def check_environment_advanced(self, temp, ph, humidity, clay_percent):
        reasons = []
        is_suitable = True
        
        if not (self.min_temp <= temp <= self.max_temp):
            is_suitable = False
            reasons.append(f"Nhiệt độ {temp}°C không nằm trong khoảng ({self.min_temp}-{self.max_temp}°C)")
            
        if not (self.min_ph <= ph <= self.max_ph):
            is_suitable = False
            reasons.append(f"Độ pH {ph} không nằm trong khoảng ({self.min_ph}-{self.max_ph})")
            
        if not (self.min_humidity <= humidity <= self.max_humidity):
            is_suitable = False
            reasons.append(f"Độ ẩm {humidity}% không phù hợp (Cần {self.min_humidity}-{self.max_humidity}%)")
            
        if clay_percent > self.max_clay:
            is_suitable = False 
            reasons.append(f"Đất quá nhiều sét ({clay_percent}%), cây này chỉ chịu được tối đa {self.max_clay}%")
            
        return is_suitable, reasons

    @property
    def total_stock(self):
        # Lazy import để tránh lỗi Circular
        from .store_stock import StoreStock
        return StoreStock.objects.filter(plant=self).aggregate(Sum('quantity'))['quantity__sum'] or 0

    @property
    def is_in_stock(self):
        return self.total_stock > 0 and self.is_available


