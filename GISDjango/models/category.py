from django.contrib.gis.db import models

class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['-id']