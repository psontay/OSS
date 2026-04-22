from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..decorators import role_required
from ..model import Plant, Order, StoreBranch

@login_required
@role_required(['admin']) # <--- Chỉ cho phép Role là 'admin' vào đây
def dashboard(request):
    # Lấy dữ liệu để đổ vào các ô Stats trên giao diện bạn ông làm
    context = {
        'total_plants': Plant.objects.count(),
        'total_orders': Order.objects.count(),
        'total_branches': StoreBranch.objects.count(),
        'recent_plants': Plant.objects.all().order_by('-id')[:5], # 5 cây mới nhất
    }
    return render(request, 'admin/dashboard.html', context)

@role_required(['admin'])
def plant_list(request):
    # Lấy toàn bộ danh sách cây để admin quản lý
    plants = Plant.objects.all().order_by('-id')
    return render(request, 'admin/plant_list.html', {'plants': plants})