from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from OSS.models import StoreBranch
from OSS.serializers import BranchSerializer
from rest_framework.permissions import IsAdminUser

@api_view(['GET'])
# @permission_classes([IsAdminUser]) # Mở ra khi bạn ông đã xử lý xong phần Token/Login
def branch_list_api(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({"status": "error", "message": "Permission denied. Admin access required."}, status=status.HTTP_403_FORBIDDEN)
    """Lấy danh sách tất cả chi nhánh"""
    items = StoreBranch.objects.all().order_by('-id')
    serializer = BranchSerializer(items, many=True)
    return Response({
        "status": "success",
        "data": serializer.data
    })

@api_view(['POST'])
def branch_create_api(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({"status": "error", "message": "Permission denied. Admin access required."}, status=status.HTTP_403_FORBIDDEN)
    """Tạo mới chi nhánh"""
    serializer = BranchSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Tạo chi nhánh mới thành công!",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({
        "status": "error",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH'])
def branch_detail_api(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({"status": "error", "message": "Permission denied. Admin access required."}, status=status.HTTP_403_FORBIDDEN)
    """Xem chi tiết hoặc Cập nhật một chi nhánh cụ thể"""
    obj = get_object_or_404(StoreBranch, pk=pk)

    if request.method == 'GET':
        serializer = BranchSerializer(obj)
        return Response({"status": "success", "data": serializer.data})

    # Cập nhật (PUT là thay hết, PATCH là thay một phần)
    serializer = BranchSerializer(instance=obj, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Cập nhật chi nhánh thành công!",
            "data": serializer.data
        })

    return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def branch_delete_api(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({"status": "error", "message": "Permission denied. Admin access required."}, status=status.HTTP_403_FORBIDDEN)
    """Xóa chi nhánh"""
    obj = get_object_or_404(StoreBranch, pk=pk)
    obj.delete()
    return Response({
        "status": "success",
        "message": f"Đã xóa chi nhánh {pk} thành công!"
    }, status=status.HTTP_204_NO_CONTENT)