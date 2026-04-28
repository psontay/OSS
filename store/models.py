from django.contrib.gis.db import models

class SoilRegion(models.Model):
    name = models.CharField(max_length=100)
    ph_level = models.FloatField()
    geom = models.PolygonField(srid=4326) 

    def __str__(self):
        return self.name

class Plant(models.Model):
    name = models.CharField(max_length=100)
    min_ph = models.FloatField()
    max_ph = models.FloatField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def is_suitable(self, soil_ph):
        return self.min_ph <= soil_ph <= self.max_ph