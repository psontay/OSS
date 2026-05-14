from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from ..models.plant import Plant
from ..models.order import Order
from ..models.store_branch import StoreBranch
from ..serializers import PlantSerializer

@api_view(['GET'])
# @permission_classes([IsAdminUser])
def dashboard_api(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({"status": "error", "message": "Permission denied. Admin access required."}, status=status.HTTP_403_FORBIDDEN)
    """
    Cung cấp các con số thống kê (Stats) cho trang chủ Admin
    """
    total_plants = Plant.objects.count()
    total_orders = Order.objects.count()
    total_branches = StoreBranch.objects.count()

    recent_plants_qs = Plant.objects.all().order_by('-id')[:5]
    recent_plants_serializer = PlantSerializer(
        recent_plants_qs,
        many=True,
        context={'request': request}
    )

    return Response({
        "status": "success",
        "data": {
            "stats": {
                "total_plants": total_plants,
                "total_orders": total_orders,
                "total_branches": total_branches,
                "total_revenue": 0,
            },
            "recent_plants": recent_plants_serializer.data
        }
    })

@api_view(['GET'])
def plant_list_api(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({"status": "error", "message": "Permission denied. Admin access required."}, status=status.HTTP_403_FORBIDDEN)
    """
    Lấy toàn bộ danh sách cây để hiển thị trong bảng quản lý
    """
    plants = Plant.objects.all().order_by('-id')
    serializer = PlantSerializer(plants, many=True, context={'request': request})

    return Response({
        "status": "success",
        "count": plants.count(),
        "data": serializer.data
    })