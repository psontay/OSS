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
    """
    Lấy danh sách tất cả đơn hàng cho Admin
    """
    orders = Order.objects.all().order_by('-created_at')
    # many=True vì trả về một danh sách
    serializer = OrderSerializer(orders, many=True)

    return Response({
        "status": "success",
        "count": orders.count(),
        "data": serializer.data
    })

@api_view(['GET'])
def order_detail_api(request, pk):
    """
    Xem chi tiết một đơn hàng (bao gồm cả danh sách món hàng items)
    """
    order = get_object_or_404(Order, pk=pk)
    serializer = OrderSerializer(order)
    return Response({
        "status": "success",
        "data": serializer.data
    })

@api_view(['PATCH']) # Dùng PATCH vì mình chỉ cập nhật một trường duy nhất là 'status'
def order_update_status_api(request, pk):
    """
    Cập nhật trạng thái đơn hàng (Đang chờ -> Đang xử lý -> Đã giao...)
    """
    order = get_object_or_404(Order, pk=pk)

    # Lấy status mới từ body JSON bạn ông gửi lên
    new_status = request.data.get('status')

    if not new_status:
        return Response({
            "status": "error",
            "message": "Thiếu thông tin trạng thái (status)!"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Ép kiểu hoa để đồng bộ với logic mình đã làm hôm trước
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