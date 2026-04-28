from django.contrib.gis.geos import Point
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.conf import settings
from django.views.decorators.http import require_POST
from geopy import Nominatim
from django.contrib.gis.db.models.functions import Distance
from ..models import Order, OrderItem, Plant, StoreStock
from .cart_controller import Cart


@login_required(login_url='login')
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Giỏ hàng của ông đang trống, mua thêm cây đi nhé!")
        return redirect('product_list')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # 1. Chuyển địa chỉ sang tọa độ GIS
        user_location = get_coords_from_address(address)
        if not user_location:
            messages.error(request, "Không thể xác định vị trí của địa chỉ này. Ông kiểm tra lại xem gõ đúng chưa?")
            return redirect('checkout')

        try:
            with transaction.atomic():
                # 2. Tính toán giá trị và chuẩn bị dữ liệu
                total_price = 0
                items_data = []
                for plant_id, item_data in cart.cart.items():
                    plant = get_object_or_404(Plant, id=plant_id)
                    subtotal = plant.price * item_data['quantity']
                    total_price += subtotal
                    items_data.append({
                        'plant': plant,
                        'quantity': item_data['quantity'],
                        'price': plant.price
                    })

                # 3. Tạo bản ghi Đơn hàng
                order = Order.objects.create(
                    user=request.user,
                    full_name=full_name,
                    phone=phone,
                    address=address,
                    total_price=total_price
                )

                # 4. Trừ kho theo logic GIS (Chi nhánh gần nhất)
                for item in items_data:
                    OrderItem.objects.create(
                        order=order,
                        plant=item['plant'],
                        price=item['price'],
                        quantity=item['quantity']
                    )

                    remaining_to_deduct = item['quantity']

                    # QUAN TRỌNG: Lấy chi nhánh có hàng và SẮP XẾP THEO KHOẢNG CÁCH
                    # Sử dụng tọa độ user_location đã lấy ở trên
                    stocks = StoreStock.objects.filter(
                        plant=item['plant'],
                        quantity__gt=0
                    ).annotate(
                        dist=Distance('branch__location', user_location)
                    ).order_by('dist')

                    for stock in stocks:
                        if remaining_to_deduct <= 0:
                            break

                        if stock.quantity >= remaining_to_deduct:
                            stock.quantity -= remaining_to_deduct
                            stock.save()
                            remaining_to_deduct = 0
                        else:
                            remaining_to_deduct -= stock.quantity
                            stock.quantity = 0
                            stock.save()

                    if remaining_to_deduct > 0:
                        raise Exception(f"Cây {item['plant'].name} không đủ hàng tại các chi nhánh lân cận!")

                # 5. Hoàn tất
                request.session[settings.CART_SESSION_ID] = {}
                request.session.modified = True
                messages.success(request, f"Đặt hàng thành công! Mã đơn: #{order.id}")
                return redirect('order_success')

        except Exception as e:
            messages.error(request, f"Lỗi: {str(e)}")
            return redirect('cart_detail')

    # Logic GET (hiển thị trang) giữ nguyên như cũ...
    # ...

    # --- XỬ LÝ LÚC MỚI VÀO TRANG (GET) ---
    # Chuẩn bị dữ liệu hiển thị tóm tắt đơn hàng bên cột phải
    cart_items = []
    total_price = 0
    for plant_id, item_data in cart.cart.items():
        plant = get_object_or_404(Plant, id=plant_id)
        subtotal = plant.price * item_data['quantity']
        total_price += subtotal
        cart_items.append({
            'plant': plant,
            'quantity': item_data['quantity'],
            'subtotal': subtotal
        })

    # Lấy thông tin mặc định từ Profile của Phạm Sơn Tây
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'default_name': f"{request.user.last_name} {request.user.first_name}".strip(),
        'default_phone': request.user.phone_number,
        'default_address': request.user.address,
    }
    return render(request, 'order/checkout.html', context)


@login_required
def order_success(request):
    return render(request, 'order/success.html')


@login_required
def order_list(request):
    """Trang xem lịch sử các đơn hàng đã mua"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order/order_list.html', {'orders': orders})
@login_required
def order_detail(request, order_id):
    """Hiển thị chi tiết một đơn hàng cụ thể"""
    # Đảm bảo chỉ chủ nhân đơn hàng mới xem được
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order/order_detail.html', {'order': order})
def get_coords_from_address(address_str):
    """Hàm chuyển địa chỉ chữ sang tọa độ Point"""
    try:
        geolocator = Nominatim(user_agent="green_shop_gis")
        # Giới hạn tìm kiếm ở Việt Nam để chính xác hơn
        location = geolocator.geocode(address_str + ", Việt Nam")
        if location:
            # Point(lng, lat)
            return Point(location.longitude, location.latitude, srid=4326)
    except Exception as e:
        print(f"Lỗi Geocoding: {e}")
    return None

@login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # 1. Kiểm tra trạng thái (Dùng .upper() để tránh lỗi chữ hoa/thường)
    if order.status.upper() != 'PENDING':
        messages.error(request, "Đơn hàng này không còn ở trạng thái Chờ xử lý nên không thể hủy.")
        return redirect('user_order_list')

    try:
        with transaction.atomic():
            # 2. LẤY DANH SÁCH MÓN HÀNG (Dùng đúng related_name='items' ông đã đặt)
            # Nếu lỡ báo lỗi tiếp, ông hãy thử thay '.items' bằng '.orderitem_set'
            order_items = order.items.all()

            for item in order_items:
                # Tìm bản ghi kho để cộng lại
                stock_record = StoreStock.objects.filter(plant=item.plant).first()
                if stock_record:
                    stock_record.quantity += item.quantity
                    stock_record.save()

                # Đồng bộ luôn kho tổng ở bảng Plant
                item.plant.stock_quantity += item.quantity
                item.plant.save()

            # 3. Chốt trạng thái HỦY
            order.status = 'CANCELLED'
            order.save()

            messages.success(request, f"Đã hủy đơn hàng #{order.id} và hoàn lại {order_items.count()} món hàng vào kho.")

    except Exception as e:
        messages.error(request, f"Lỗi hệ thống: {str(e)}")

    return redirect('user_order_list')