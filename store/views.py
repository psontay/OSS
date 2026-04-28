from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.gis.geos import Point
from .models import SoilRegion, Plant

def home(request):
    return render(request, 'index.html')

def product_list(request):
    # Lấy toàn bộ cây cảnh để hiển thị ở trang shop
    plants = Plant.objects.all()
    return render(request, 'product_list.html', {'plants': plants})

def suitability_page(request):
    # Trả về trang có bản đồ Leaflet đã tách ra
    return render(request, 'check_suitability.html')

def check_suitability(request):
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
        plant_id = request.GET.get('plant_id')
        
        user_location = Point(lng, lat, srid=4326)
        region = SoilRegion.objects.filter(geom__contains=user_location).first()
        
        if region:
            plant = get_object_or_404(Plant, id=plant_id)
            suitable = plant.is_suitable(region.ph_level)
            return JsonResponse({
                'status': 'success',
                'region': region.name,
                'ph': region.ph_level,
                'suitable': suitable,
                'message': "Đất phù hợp!" if suitable else "Đất không phù hợp."
            })
        return JsonResponse({'status': 'error', 'message': 'Khu vực này chưa có dữ liệu đất.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})