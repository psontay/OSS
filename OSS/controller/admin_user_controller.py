from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser

from OSS.models import User
from OSS.serializers import UserSerializer

@api_view(['GET'])
# @permission_classes([IsAdminUser])
def user_list_api(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({"status": "error", "message": "Permission denied. Admin access required."}, status=status.HTTP_403_FORBIDDEN)
    """Lấy danh sách tất cả người dùng"""
    users = User.objects.all().order_by('-id')
    serializer = UserSerializer(users, many=True)
    return Response({
        "status": "success",
        "data": serializer.data
    })

@api_view(['DELETE'])
# @permission_classes([IsAdminUser])
def user_delete_api(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({"status": "error", "message": "Permission denied. Admin access required."}, status=status.HTTP_403_FORBIDDEN)
    """Xóa người dùng (không cho xóa superuser)"""
    user = get_object_or_404(User, pk=pk)
    if user.is_superuser:
        return Response({
            "status": "error",
            "message": "Không thể xóa tài khoản Quản trị tối cao!"
        }, status=status.HTTP_400_BAD_REQUEST)

    user.delete()
    return Response({
        "status": "success",
        "message": f"Đã xóa người dùng {user.username} thành công!"
    })