from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..models.store_stock import StoreStock
from ..serializers import StoreStockSerializer
from ..utils import log_stock_action_to_excel  # Import hàm log hôm nọ ông viết
from rest_framework.permissions import IsAdminUser

@api_view(['GET'])
# @permission_classes([IsAdminUser])
def stock_list_api(request):
    """Lấy danh sách tồn kho của tất cả chi nhánh và sản phẩm"""
    stocks = StoreStock.objects.select_related('branch', 'plant').all().order_by('branch__name')
    serializer = StoreStockSerializer(stocks, many=True)
    return Response({
        "status": "success",
        "count": stocks.count(),
        "data": serializer.data
    })

@api_view(['POST'])
def stock_create_api(request):
    """Tạo bản ghi kho mới (Gán một cây vào một chi nhánh)"""
    serializer = StoreStockSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Đã thêm mới bản ghi kho thành công!",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH'])
def stock_detail_api(request, pk):
    """Xem hoặc cập nhật số lượng tồn kho"""
    stock = get_object_or_404(StoreStock, pk=pk)

    if request.method == 'GET':
        serializer = StoreStockSerializer(stock)
        return Response({"status": "success", "data": serializer.data})

    # Logic Cập nhật số lượng
    old_qty = stock.quantity
    new_qty = request.data.get('quantity')

    if new_qty is None:
        return Response({"status": "error", "message": "Vui lòng cung cấp số lượng mới!"}, status=status.HTTP_400_BAD_REQUEST)

    # 1. Cập nhật vào DB
    stock.quantity = new_qty
    stock.save()

    # 2. Ghi nhật ký vào file Excel (Sử dụng hàm utils của ông)
    try:
        log_stock_action_to_excel(
            user_name=request.user.username if request.user.is_authenticated else "Admin_API",
            action="UPDATE_STOCK",
            plant_name=stock.plant.name,
            branch_name=stock.branch.name,
            old_qty=old_qty,
            new_qty=new_qty
        )
    except Exception as e:
        print(f"Lỗi ghi log Excel: {e}")

    serializer = StoreStockSerializer(stock)
    return Response({
        "status": "success",
        "message": f"Đã cập nhật tồn kho thành công! ({old_qty} -> {new_qty})",
        "data": serializer.data
    })

@api_view(['DELETE'])
def stock_delete_api(request, pk):
    """Xóa một bản ghi kho (Cẩn thận khi dùng)"""
    stock = get_object_or_404(StoreStock, pk=pk)
    stock.delete()
    return Response({
        "status": "success",
        "message": "Đã xóa bản ghi kho thành công!"
    }, status=status.HTTP_204_NO_CONTENT)