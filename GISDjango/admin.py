from django.contrib.gis import admin
from .models.plant import Plant
from .models.category import Category

@admin.register(Plant)
class PlantAdmin(admin.GISModelAdmin):
    list_display = ('name', 'price', 'category', 'location')
    search_fields = ('name',)
    list_filter = ('category',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')