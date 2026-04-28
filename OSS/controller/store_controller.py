from unicodedata import category

from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.gis.geos import Point
from ..model.plant import Plant, SoilRegion
from ..model.plant_img import PlantImage
from django.shortcuts import render
from ..model import StoreBranch, StoreStock, Category
from .cart_controller import Cart
import json
from django.core.paginator import Paginator

def home(request):
    plantsHot = Plant.objects.all()
    return render(request, 'pages/home.html', {'plantsHot': plantsHot})


def product_list(request, category_slug=None):
    cart = Cart(request)
    total_items = len(cart)
    categories = Category.objects.all()
    plants = Plant.objects.all().order_by('-id')
    selected_category = None
    branches = StoreBranch.objects.filter(is_active=True)
    selected_branch_id = request.GET.get('branch') # Lấy ID chi nhánh từ URL (?branch=1)

    ph_value = request.GET.get('ph')

    # 1. Lọc theo danh mục
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        plants = plants.filter(category=selected_category)

    # 2. Lọc theo chi nhánh (QUAN TRỌNG)
    if selected_branch_id:
        # Lọc những cây có bản ghi StoreStock tại chi nhánh này và số lượng > 0
        plants = plants.filter(
            storestock__branch_id=selected_branch_id,
            storestock__quantity__gt=0
        ).distinct() # Dùng distinct để tránh bị lặp cây nếu dữ liệu lỗi

    # 3. Logic lọc theo độ pH
    if ph_value:
        try:
            ph_float = float(ph_value)
            plants = plants.filter(min_ph__lte=ph_float, max_ph__gte=ph_float)
        except ValueError:
            ph_value = None

    # --- BẮT ĐẦU LOGIC PHÂN TRANG ---
    # Mỗi trang hiện 9 cây (thường là 3x3 cho đẹp giao diện)
    paginator = Paginator(plants, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # --------------------------------

    return render(request, 'products/product_list.html', {
        'total_items': total_items,
        'categories': categories,
        'branches': branches,
        'page_obj': page_obj,  # Dùng page_obj thay vì plants để loop ở template
        'selected_category': selected_category,
        'current_ph': ph_value
    })


def product_detail(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id)  # Debug: Kiểm tra dữ liệu ảnh
    images = PlantImage.objects.filter(plant=plant)
    # Lấy thông tin tồn kho chi tiết từng chi nhánh
    stocks = StoreStock.objects.filter(plant=plant, quantity__gt=0)
    # Tính tổng tồn kho
    total_stock = stocks.aggregate(Sum('quantity'))['quantity__sum'] or 0

    return render(request, 'products/product_detail.html', {
        'plant': plant,
        'stocks': stocks,
        'total_stock': total_stock,
        'images': images
    })

def suitability_page(request):
    # Trả về trang có bản đồ Leaflet đã tách ra
    return render(request, 'gis/check_suitability.html')

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


def store_locations_map(request):
    branches = StoreBranch.objects.filter(is_active=True)

    branch_list = []
    for b in branches:
        if b.location:
            branch_list.append({
                'name': b.name,
                'address': b.address,
                'phone': b.phone or "Liên hệ trực tiếp",
                'opening_hours': b.opening_hours or "Đang cập nhật",
                'lat': b.location.y,
                'lng': b.location.x,
                'radius': b.delivery_radius
            })
    return render(request, 'gis/store_map.html', {
        'branches_json': json.dumps(branch_list)
    })