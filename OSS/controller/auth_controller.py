from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from ..serializers import UserSerializer

@api_view(['POST'])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user:
        if not user.is_active:
            return Response({
                "status": "warning",
                "message": "Tài khoản chưa kích hoạt!",
                "user_id": user.id
            }, status=status.HTTP_403_FORBIDDEN)

        # TẠO TOKEN Ở ĐÂY NÈ TÂY
        refresh = RefreshToken.for_user(user)
        serializer = UserSerializer(user)

        return Response({
            "status": "success",
            "message": "Đăng nhập thành công!",
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            "user": serializer.data,
            "is_admin": user.is_staff
        })

    return Response({
        "status": "error",
        "message": "Tên đăng nhập hoặc mật khẩu không chính xác!"
    }, status=status.HTTP_401_UNAUTHORIZED)