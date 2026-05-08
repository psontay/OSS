from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Sum
from decimal import Decimal

from ..models import StoreStock, StoreBranch, Order, OrderItem, Plant
from ..serializers import OrderSerializer, CheckoutInputSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_checkout(request):
    """
    API Thanh toán: Nhận JSON giỏ hàng và thông tin giao hàng
    """
    serializer = CheckoutInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    items_data = data['items']
    location_coord = data['location_coord']

    try:
        # 1. Xử lý tọa độ GIS
        lat_str, lng_str = location_coord.split(',')
        customer_pnt = Point(float(lng_str), float(lat_str), srid=4326)

        # 2. Tìm chi nhánh gần nhất (Bán kính 10km)
        nearest_branch = StoreBranch.objects.annotate(
            distance=Distance('location', customer_pnt, spheroid=True)
        ).filter(distance__lte=D(km=10)).order_by('distance').first()

        if not nearest_branch:
            return Response({"message": "Địa chỉ nằm ngoài vùng phục vụ (10km)."}, status=400)

        # 3. Tính phí ship
        distance_km = nearest_branch.distance.km
        ship_fee = Decimal('0')
        if distance_km > 2:
            raw_fee = (distance_km - 2) * 5000
            ship_fee = Decimal(str(round(raw_fee, -3)))
            if ship_fee < 15000: ship_fee = Decimal('15000')

        # 4. Kiểm tra kho và chuẩn bị dữ liệu trong Transaction
        total_price = Decimal('0')
        order_items_to_create = []

        with transaction.atomic():
            for item in items_data:
                plant = get_object_or_404(Plant, id=item['plant_id'])
                qty = item['quantity']

                # Check tổng kho
                total_stock = StoreStock.objects.filter(plant=plant).aggregate(Sum('quantity'))['quantity__sum'] or 0
                if qty > total_stock:
                    raise Exception(f"Sản phẩm {plant.name} không đủ hàng (Còn {total_stock})")

                subtotal = plant.price * qty
                total_price += subtotal

                order_items_to_create.append({
                    'plant': plant,
                    'quantity': qty,
                    'price': plant.price
                })

            # 5. Tạo đơn hàng
            order = Order.objects.create(
                user=request.user,
                full_name=data['full_name'],
                email=request.user.email,
                phone=data['phone'],
                address=data['address'],
                shipping_fee=ship_fee,
                delivery_location=customer_pnt,
                total_price=total_price + ship_fee,
                status='PENDING'
            )

            # 6. Trừ kho đa chi nhánh (Logic xịn của Tây)
            for item in order_items_to_create:
                remaining = item['quantity']
                all_stocks = StoreStock.objects.filter(plant=item['plant']).annotate(
                    distance=Distance('branch__location', customer_pnt, spheroid=True)
                ).order_by('distance')

                for stock in all_stocks:
                    if remaining <= 0: break
                    if stock.quantity >= remaining:
                        stock.quantity -= remaining
                        stock.save()
                        remaining = 0
                    else:
                        remaining -= stock.quantity
                        stock.quantity = 0
                        stock.save()

                if remaining > 0:
                    raise Exception(f"Lỗi kho cho sản phẩm {item['plant'].name}")

                # Tạo OrderItem
                OrderItem.objects.create(
                    order=order,
                    plant=item['plant'],
                    quantity=item['quantity'],
                    price=item['price']
                )

        return Response({
            "status": "success",
            "message": "Đặt hàng thành công!",
            "order_id": order.id,
            "shipping_fee": float(ship_fee)
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_orders(request):
    """Lấy danh sách đơn hàng của tôi"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response({"status": "success", "data": serializer.data})