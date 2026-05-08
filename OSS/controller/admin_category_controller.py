from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from OSS.models.category import Category
from OSS.serializers import CategorySerializer
from rest_framework.permissions import IsAdminUser

@api_view(['GET'])
# @permission_classes([IsAdminUser])
def category_list_api(request):
    """Lấy danh sách tất cả danh mục"""
    items = Category.objects.all().order_by('id')
    serializer = CategorySerializer(items, many=True)
    return Response({
        "status": "success",
        "count": items.count(),
        "data": serializer.data
    })

@api_view(['POST'])
def category_create_api(request):
    """Tạo mới một danh mục"""
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Thêm danh mục mới thành công!",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({
        "status": "error",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH'])
def category_detail_api(request, pk):
    """Xem chi tiết hoặc Cập nhật danh mục"""
    obj = get_object_or_404(Category, pk=pk)

    if request.method == 'GET':
        serializer = CategorySerializer(obj)
        return Response({"status": "success", "data": serializer.data})

    # Cập nhật danh mục (Dùng PATCH để cập nhật từng phần cho linh hoạt)
    serializer = CategorySerializer(instance=obj, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Cập nhật danh mục thành công!",
            "data": serializer.data
        })

    return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def category_delete_api(request, pk):
    """Xóa danh mục"""
    obj = get_object_or_404(Category, pk=pk)

    # Kiểm tra xem danh mục có đang chứa cây nào không (Ràng buộc dữ liệu)
    if obj.plant_set.exists():
        return Response({
            "status": "error",
            "message": "Không thể xóa danh mục này vì vẫn còn sản phẩm bên trong!"
        }, status=status.HTTP_400_BAD_REQUEST)

    obj.delete()
    return Response({
        "status": "success",
        "message": f"Đã xóa danh mục '{obj.name}' thành công!"
    }, status=status.HTTP_204_NO_CONTENT)