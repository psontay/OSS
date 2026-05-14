from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..models.order import Order
from ..serializers import OrderSerializer
from rest_framework.permissions import IsAdminUser

@api_view(['GET'])
# @permission_classes([IsAdminUser])
def order_list_api(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({"status": "error", "message": "Permission denied. Admin access required."}, status=status.HTTP_403_FORBIDDEN)
    """
    Lấy danh sách tất cả đơn hàng cho Admin
    """
    orders = Order.objects.all().order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)

    return Response({
        "status": "success",
        "count": orders.count(),
        "data": serializer.data
    })

@api_view(['GET'])
def order_detail_api(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({"status": "error", "message": "Permission denied. Admin access required."}, status=status.HTTP_403_FORBIDDEN)
    """
    Xem chi tiết một đơn hàng (bao gồm cả danh sách món hàng items)
    """
    order = get_object_or_404(Order, pk=pk)
    serializer = OrderSerializer(order)
    return Response({
        "status": "success",
        "data": serializer.data
    })

@api_view(['PATCH'])
def order_update_status_api(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({"status": "error", "message": "Permission denied. Admin access required."}, status=status.HTTP_403_FORBIDDEN)
    """
    Cập nhật trạng thái đơn hàng (Đang chờ -> Đang xử lý -> Đã giao...)
    """
    order = get_object_or_404(Order, pk=pk)

    new_status = request.data.get('status')
    if not new_status:
        return Response({
            "status": "error",
            "message": "Thiếu thông tin trạng thái (status)!"
        }, status=status.HTTP_400_BAD_REQUEST)

    order.status = new_status.upper()
    order.save()

    return Response({
        "status": "success",
        "message": f"Đã cập nhật trạng thái đơn hàng #{pk} thành {order.status}",
        "data": {
            "id": order.id,
            "new_status": order.status
        }
    })