from django.shortcuts import render, get_object_or_404, redirect

from ..decorators import role_required
from ..model.order import Order


@role_required(allowed_roles=['admin'])
def order_list(request):
    items = Order.objects.all().order_by('-created_at')
    return render(request, 'admin/order/list.html', {'items': items})

@role_required(allowed_roles=['admin'])
def order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.status = request.POST.get('status')
        order.save()
    return redirect('admin_order_list')
