from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name="Tên danh mục")
    
    slug = models.SlugField(unique=True, max_length=255, blank=True, null=True, verbose_name="Link thân thiện")
    
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả danh mục")
    
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Ảnh đại diện")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-id']