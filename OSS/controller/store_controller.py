from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.contrib.gis.geos import Point
from rest_framework.pagination import PageNumberPagination

from ..models import Plant, Category, StoreBranch, StoreStock, PlantImage
from ..models.plant import SoilRegion
from ..serializers import PlantSerializer, CategorySerializer, BranchSerializer

# --- PHÂN TRANG CUSTOM ---
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 6 # Giữ nguyên 6 cây mỗi trang như ông yêu cầu
    page_size_query_param = 'page_size'
    max_page_size = 100

# --- API ENDPOINTS ---

@api_view(['GET'])
def home_api(request):
    """API cho trang chủ: Lấy danh sách cây hot/mới nhất"""
    plants = Plant.objects.all().order_by('-id')[:8]
    serializer = PlantSerializer(plants, many=True, context={'request': request})
    return Response({
        "status": "success",
        "data": serializer.data
    })

@api_view(['GET'])
def product_list_api(request):
    """
    API Danh sách sản phẩm: Lọc theo Category, Branch, pH và có Phân trang
    """
    plants = Plant.objects.all().order_by('-id')

    # 1. Lấy params từ URL
    category_slug = request.query_params.get('category')
    branch_id = request.query_params.get('branch')
    ph_value = request.query_params.get('ph')

    # 2. Lọc theo Category
    if category_slug:
        plants = plants.filter(category__slug=category_slug)

    # 3. Lọc theo Chi nhánh (Còn hàng)
    if branch_id:
        plants = plants.filter(storestock__branch_id=branch_id, storestock__quantity__gt=0).distinct()

    # 4. Lọc theo độ pH
    if ph_value:
        try:
            ph_float = float(ph_value)
            plants = plants.filter(min_ph__lte=ph_float, max_ph__gte=ph_float)
        except ValueError:
            pass

    # 5. Phân trang theo chuẩn DRF
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(plants, request)
    serializer = PlantSerializer(result_page, many=True, context={'request': request})

    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def product_detail_api(request, pk):
    """API Chi tiết sản phẩm: Trả về cả ảnh phụ và tồn kho"""
    plant = get_object_or_404(Plant, id=pk)

    # Lấy tồn kho thực tế
    stocks = StoreStock.objects.filter(plant=plant, quantity__gt=0)
    total_stock = stocks.aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Lấy danh sách ảnh phụ
    images = PlantImage.objects.filter(plant=plant)
    image_urls = [request.build_absolute_uri(img.image.url) for img in images if img.image]

    serializer = PlantSerializer(plant, context={'request': request})

    # Gộp thêm thông tin vào JSON trả về
    data = serializer.data
    data['total_stock'] = total_stock
    data['sub_images'] = image_urls
    data['stock_detail'] = [
        {"branch_name": s.branch.name, "quantity": s.quantity} for s in stocks
    ]

    return Response({"status": "success", "data": data})

@api_view(['GET'])
def check_suitability_api(request):
    """
    GIS API: Kiểm tra cây có hợp với vùng đất (lat, lng) không
    """
    try:
        lat = float(request.query_params.get('lat'))
        lng = float(request.query_params.get('lng'))
        plant_id = request.query_params.get('plant_id')

        user_location = Point(lng, lat, srid=4326)
        region = SoilRegion.objects.filter(geom__contains=user_location).first()

        if region:
            plant = get_object_or_404(Plant, id=plant_id)
            suitable = plant.is_suitable(region.ph_level)
            return Response({
                'status': 'success',
                'region': region.name,
                'ph': region.ph_level,
                'suitable': suitable,
                'message': "Đất phù hợp!" if suitable else "Đất không phù hợp cho cây này."
            })
        return Response({'status': 'error', 'message': 'Khu vực này chưa có dữ liệu đất.'}, status=404)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)

@api_view(['GET'])
def store_locations_api(request):
    """API trả về tọa độ các chi nhánh để vẽ lên bản đồ"""
    branches = StoreBranch.objects.filter(is_active=True)
    branch_data = []
    for b in branches:
        if b.location:
            branch_data.append({
                'id': b.id,
                'name': b.name,
                'address': b.address,
                'lat': b.location.y,
                'lng': b.location.x,
                'radius': b.delivery_radius
            })
    return Response({"status": "success", "data": branch_data})