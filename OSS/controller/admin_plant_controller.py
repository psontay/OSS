from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..models.plant import Plant
from ..serializers import PlantSerializer
from rest_framework.permissions import IsAdminUser

@api_view(['GET'])
# @permission_classes([IsAdminUser])
def plant_list_api(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({"status": "error", "message": "Permission denied. Admin access required."}, status=status.HTTP_403_FORBIDDEN)
    """Lấy danh sách tất cả sản phẩm cây cảnh"""
    items = Plant.objects.select_related('category').all().order_by('-id')
    # Lưu ý: context={'request': request} để Serializer tạo URL ảnh tuyệt đối
    serializer = PlantSerializer(items, many=True, context={'request': request})
    return Response({
        "status": "success",
        "count": items.count(),
        "data": serializer.data
    })

@api_view(['POST'])
def plant_create_api(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({"status": "error", "message": "Permission denied. Admin access required."}, status=status.HTTP_403_FORBIDDEN)
    """Tạo mới một sản phẩm (Có kèm upload ảnh)"""
    # Custom validations
    min_ph = request.data.get('min_ph')
    max_ph = request.data.get('max_ph')
    price = request.data.get('price')
    
    if min_ph is not None and max_ph is not None and float(min_ph) > float(max_ph):
        return Response({
            "status": "error",
            "message": "min_ph must be less than or equal to max_ph"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if price is not None and float(price) <= 0:
        return Response({
            "status": "error",
            "message": "price must be greater than 0"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = PlantSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Thêm cây mới thành công!",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({
        "status": "error",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH'])
def plant_detail_api(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({"status": "error", "message": "Permission denied. Admin access required."}, status=status.HTTP_403_FORBIDDEN)
    """Xem chi tiết hoặc Cập nhật thông tin cây"""
    obj = get_object_or_404(Plant, pk=pk)

    if request.method == 'GET':
        serializer = PlantSerializer(obj, context={'request': request})
        return Response({"status": "success", "data": serializer.data})

    # Cập nhật (PATCH cho phép gửi chỉ những trường cần thay đổi, ví dụ chỉ gửi giá mới)
    serializer = PlantSerializer(instance=obj, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Cập nhật thông tin cây thành công!",
            "data": serializer.data
        })

    return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def plant_delete_api(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({"status": "error", "message": "Permission denied. Admin access required."}, status=status.HTTP_403_FORBIDDEN)
    """Xóa sản phẩm cây cảnh"""
    obj = get_object_or_404(Plant, pk=pk)
    # Lưu ý: Cân nhắc logic xóa ảnh trong thư mục media nếu cần thiết tại đây
    obj.delete()
    return Response({
        "status": "success",
        "message": f"Đã xóa cây '{obj.name}' khỏi hệ thống!"
    }, status=status.HTTP_204_NO_CONTENT)