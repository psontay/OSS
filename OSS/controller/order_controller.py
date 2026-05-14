from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from geopy import Nominatim

from ..models import Order, OrderItem, Plant, StoreStock
from ..serializers import OrderSerializer

# --- HÀM UTILS (GIỮ NGUYÊN LOGIC GIS) ---
def get_coords_from_address(address_str):
    """Thử geocode địa chỉ. Trả về Point nếu thành công, None nếu thất bại."""
    try:
        geolocator = Nominatim(user_agent="green_shop_gis", timeout=5)
        # Thử địa chỉ đầy đủ trước
        location = geolocator.geocode(address_str + ", Việt Nam")
        if location:
            return Point(location.longitude, location.latitude, srid=4326)
        # Fallback: chỉ lấy phần thành phố/tỉnh (chuỗi cuối cùng sau dấu phẩy)
        parts = [p.strip() for p in address_str.split(',')]
        if len(parts) > 1:
            # Thử với 2 phần cuối
            short_addr = ', '.join(parts[-2:])
            location = geolocator.geocode(short_addr + ", Việt Nam")
            if location:
                return Point(location.longitude, location.latitude, srid=4326)
        return None
    except Exception as e:
        print(f"Lỗi Geocoding: {e}")
    return None

# Tọa độ mặc định cho TP. Hồ Chí Minh khi không geocode được
DEFAULT_LOCATION = Point(106.660172, 10.762622, srid=4326)

# --- API ENDPOINTS ---

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_checkout(request):
    """
    API đặt hàng.
    Frontend gửi: { "full_name": "...", "phone": "...", "address": "...", "items": [{"id": 1, "qty": 2}, ...] }
    """
    data = request.data
    items_input = data.get('items', [])
    address = data.get('address')

    if not items_input:
        return Response({"message": "Giỏ hàng trống!"}, status=status.HTTP_400_BAD_REQUEST)

    # 1. Xác định tọa độ GIS (ưu tiên location_coord từ frontend, fallback: geocode)
    user_location = None
    location_coord = data.get('location_coord', '')
    if location_coord:
        try:
            lat, lng = map(float, location_coord.split(','))
            user_location = Point(lng, lat, srid=4326)
        except Exception:
            pass  # fallback to geocoding
    
    if not user_location:
        user_location = get_coords_from_address(address)
    
    if not user_location:
        # Dùng tọa độ mặc định TP. Hồ Chí Minh nếu không geocode được
        user_location = DEFAULT_LOCATION

    try:
        with transaction.atomic():
            # 2. Tạo bản ghi Đơn hàng
            order = Order.objects.create(
                user=request.user,
                full_name=data.get('full_name'),
                phone=data.get('phone'),
                address=address,
                delivery_location=user_location,
                total_price=0 # Sẽ cập nhật sau khi tính item
            )

            total_price = 0
            for item in items_input:
                plant = get_object_or_404(Plant, id=item['id'])
                qty = int(item['qty'])

                # Tạo chi tiết đơn hàng
                OrderItem.objects.create(
                    order=order,
                    plant=plant,
                    price=plant.price,
                    quantity=qty
                )
                total_price += (plant.price * qty)

                # 3. Trừ kho theo logic GIS (Chi nhánh gần nhất)
                remaining_to_deduct = qty
                stocks = StoreStock.objects.filter(
                    plant=plant,
                    quantity__gt=0
                ).annotate(
                    dist=Distance('branch__location', user_location)
                ).order_by('dist')

                for stock in stocks:
                    if remaining_to_deduct <= 0: break
                    if stock.quantity >= remaining_to_deduct:
                        stock.quantity -= remaining_to_deduct
                        stock.save()
                        remaining_to_deduct = 0
                    else:
                        remaining_to_deduct -= stock.quantity
                        stock.quantity = 0
                        stock.save()

                if remaining_to_deduct > 0:
                    raise Exception(f"Cây {plant.name} không đủ hàng tại các chi nhánh!")

            # Cập nhật tổng tiền cuối cùng
            order.total_price = total_price
            order.save()

        return Response({
            "status": "success",
            "message": f"Đặt hàng thành công! Mã đơn: #{order.id}",
            "order_id": order.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_order_list(request):
    """Lấy lịch sử mua hàng của User hiện tại"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_order_detail(request, pk):
    """Xem chi tiết một đơn hàng"""
    order = get_object_or_404(Order, id=pk, user=request.user)
    serializer = OrderSerializer(order)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_cancel_order(request, pk):
    """Hủy đơn hàng và hoàn kho"""
    order = get_object_or_404(Order, id=pk, user=request.user)

    if order.status.upper() != 'PENDING':
        return Response({"message": "Chỉ có thể hủy đơn đang chờ xử lý."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            for item in order.items.all():
                # Hoàn kho tại chi nhánh mặc định hoặc chi nhánh đầu tiên (vì logic trừ kho phức tạp)
                stock_record = StoreStock.objects.filter(plant=item.plant).first()
                if stock_record:
                    stock_record.quantity += item.quantity
                    stock_record.save()

            order.status = 'CANCELLED'
            order.save()

        return Response({"status": "success", "message": "Đã hủy đơn và hoàn kho thành công."})
    except Exception as e:
        return Response({"message": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)