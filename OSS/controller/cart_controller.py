from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Point
from django.db.models.functions import Cast
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.conf import settings
from django.db.models import Sum
from ..models import StoreStock, StoreBranch
from ..models.plant import Plant
from django.contrib import messages
from ..models import Order, OrderItem
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from decimal import Decimal

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, plant, quantity=1, override_quantity=False):
        plant_id = str(plant.id)
        if plant_id not in self.cart:
            self.cart[plant_id] = {'quantity': 0, 'price': str(plant.price)}

        if override_quantity:
            self.cart[plant_id]['quantity'] = quantity
        else:
            self.cart[plant_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def remove(self, plant):
        """Xóa hẳn một sản phẩm khỏi giỏ hàng"""
        plant_id = str(plant.id)
        if plant_id in self.cart:
            del self.cart[plant_id]
            self.save()

@require_POST
def cart_add(request, plant_id):
    cart = Cart(request)
    plant = get_object_or_404(Plant, id=plant_id)
    quantity = int(request.POST.get('quantity', 1))
    override = request.POST.get('override', False)


    # 1. Lấy số lượng khách muốn mua
    quantity = int(request.POST.get('quantity', 1))
    override = request.POST.get('override') == 'True'

    # 2. Kiểm tra tổng tồn kho trên toàn hệ thống (tất cả chi nhánh)
    total_stock = StoreStock.objects.filter(plant=plant).aggregate(Sum('quantity'))['quantity__sum'] or 0

    if total_stock <= 0:
        messages.error(request, f"Rất tiếc, sản phẩm {plant.name} đã hết hàng trên toàn hệ thống!")
        return redirect('product_detail', plant_id=plant_id)

    if quantity > total_stock:
        messages.warning(request, f"Bạn muốn mua {quantity} cây, nhưng chúng tôi chỉ còn {total_stock} cây trong kho.")
        return redirect('product_detail', plant_id=plant_id)

    # 3. Nếu đủ hàng thì mới thực hiện add
    cart.add(plant=plant, quantity=quantity, override_quantity=override)

    return redirect('cart_detail')


def cart_detail(request):
    cart = Cart(request)
    cart_items = []
    total_price = 0
    for plant_id, item in cart.cart.items():
        # LƯU Ý: Nếu sau này hệ thống lớn, query từng item trong vòng lặp sẽ hơi chậm. 
        # Tạm thời với quy mô nhỏ thì cách này vẫn ổn.
        plant = Plant.objects.get(id=plant_id)
        subtotal = plant.price * item['quantity']
        total_price += subtotal
        cart_items.append({
            'plant': plant,
            'quantity': item['quantity'],
            'subtotal': subtotal
        })

    # [ĐÃ SỬA] Cập nhật đường dẫn thư mục thành 'orders/cart_detail.html'
    return render(request, 'orders/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

# Action: Xóa sản phẩm
def cart_remove(request, plant_id):
    cart = Cart(request)
    plant = get_object_or_404(Plant, id=plant_id)
    cart.remove(plant)
    return redirect('cart_detail')


from django.db import transaction
from ..models import Order, OrderItem

@login_required
def checkout(request):
    cart_obj = Cart(request)
    if len(cart_obj) == 0:
        return redirect('product_list')

    if request.method == 'POST':
        # 1. Lấy dữ liệu từ Form
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        location_coord = request.POST.get('location_coord') # Định dạng "lat,lng" từ JS

        if not location_coord:
            messages.error(request, "Vui lòng xác nhận vị trí trên bản đồ để tính phí giao hàng.")
            return redirect('checkout')

        try:
            # 2. Xử lý tọa độ khách hàng (Lưu ý: Point nhận Longitude trước, Latitude sau)
            lat_str, lng_str = location_coord.split(',')
            customer_pnt = Point(float(lng_str), float(lat_str), srid=4326)

            # 3. Tìm chi nhánh gần nhất trong bán kính 10km
            # annotate tính khoảng cách, filter chặn 10km, order_by lấy cái gần nhất
            nearest_branch = StoreBranch.objects.annotate(
                distance=Distance('location', customer_pnt, spheroid=True)
            ).filter(distance__lte=D(km=10)).order_by('distance').first()

            if not nearest_branch:
                messages.error(request, "Rất tiếc, địa chỉ của bạn nằm ngoài vùng phục vụ (bán kính 10km) của hệ thống.")
                return redirect('checkout')


            # Tính toán tổng tiền đơn hàng
            total_price = 0
            cart_items_to_save = []
            for plant_id, item_data in cart_obj.cart.items():
                plant = get_object_or_404(Plant, id=plant_id)
                subtotal = plant.price * item_data['quantity']
                total_price += subtotal
                cart_items_to_save.append({
                    'plant': plant,
                    'quantity': item_data['quantity'],
                    'price': plant.price
                })
            distance_km = nearest_branch.distance.km
            ship_fee = 0

            # Công thức tính phí ship:
            if distance_km > 2:
                # (Tổng km - 2km đầu free) * 5000đ
                raw_fee = (distance_km - 2) * 5000

                # Làm tròn lên hàng nghìn cho đẹp (ví dụ 12.400đ -> 12.000đ hoặc 13.000đ)
                ship_fee = Decimal(str(round(raw_fee, -3)))

                # Giới hạn phí ship tối thiểu nếu ông muốn (ví dụ tối thiểu 15k nếu đã tính phí)
                if ship_fee < 15000: ship_fee = 15000

            # Tính tổng tiền cuối cùng = Tiền cây + Phí ship
            final_total = total_price + ship_fee

            # 4. Tiến hành tạo đơn hàng trong một transaction
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    full_name=full_name,
                    email=request.user.email,
                    phone=phone,
                    address=address,
                    shipping_fee=ship_fee,
                    delivery_location=customer_pnt,
                    total_price=final_total,
                    status='PENDING'
                )

                # Duyệt qua giỏ hàng để trừ kho và tạo chi tiết đơn
                for item in cart_items_to_save:
                    plant = item['plant']
                    qty = item['quantity']

                    remaining_to_deduct = qty

                    # Ưu tiên trừ kho tại chi nhánh gần nhất đã tìm thấy ở trên
                    all_stocks = StoreStock.objects.filter(plant=plant).annotate(
                        distance=Distance('branch__location', customer_pnt, spheroid=True)
                    ).order_by('distance')

                    for stock in all_stocks:
                        if remaining_to_deduct <= 0: break
                        if stock.quantity >= remaining_to_deduct:
                            stock.quantity -= remaining_to_deduct
                            stock.save()
                            remaining_to_deduct = 0
                        else:
                            remaining_to_deduct -= stock.quantity
                            stock.quantity = 0
                            stock.save()
                    if remaining_to_deduct > 0:
                        raise Exception(f"Loi: Tong kho con` nhung chi nhanh het hang")

                    OrderItem.objects.create(
                        order=order,
                        plant=plant,
                        quantity=qty,
                        price=item['price']
                    )

            # Xóa giỏ hàng sau khi thành công
            request.session[settings.CART_SESSION_ID] = {}
            request.session.modified = True

            messages.success(request, f"Đặt hàng thành công! Đơn hàng sẽ được xử lý bởi chi nhánh {nearest_branch.name}.")
            return redirect('order_success')

        except Exception as e:
            messages.error(request, f"Lỗi đặt hàng: {str(e)}")
            return redirect('checkout')
    # Xử lý khi vào trang (GET)
    cart_items = []
    total_price = 0

    for plant_id, item_data in cart_obj.cart.items():
        plant = get_object_or_404(Plant, id=plant_id)
        subtotal = plant.price * item_data['quantity']
        total_price += subtotal

        cart_items.append({
            'plant': plant,
            'quantity': item_data['quantity'],
            'subtotal': subtotal
        })

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'default_name': f"{request.user.last_name} {request.user.first_name}".strip(),
        'default_phone': request.user.phone_number,
        'default_address': request.user.address,
    }

    # [ĐÃ SỬA] Đổi 'order/checkout.html' thành 'orders/checkout.html' cho đồng bộ tên thư mục
    return render(request, 'orders/checkout.html', context)
def order_success_view(request):
    return render(request, 'orders/order_success.html')

@login_required
def user_order_list(request):
    # Lấy tất cả đơn hàng mà khách hàng này đã đặt (lọc theo email hoặc user)
    # Sắp xếp theo thời gian mới nhất hiện lên đầu
    orders = Order.objects.filter(email=request.user.email).order_by('-created_at')

    return render(request, 'orders/user_order_list.html', {
        'orders': orders
    })

@login_required
def user_order_detail(request, order_id):
    # Đảm bảo khách chỉ xem được đơn của chính mình (lọc theo email hoặc user)
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # [LƯU Ý] Nếu ông để file template ở thư mục orders/ thì để là 'orders/order_detail.html'
    return render(request, 'orders/order_detail.html', {'order': order})