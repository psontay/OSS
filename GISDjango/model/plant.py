from django.contrib.gis.db import models
class Plant(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    location = models.PointField(srid=4326)
    min_temp = models.FloatField(default=20.0)
    max_temp = models.FloatField(default=35.0)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return self.name