from ..decorators import role_required
from ..model.store_stock import StoreStock
from admin_forms import StockForm
from django.shortcuts import render, get_object_or_404, redirect


@role_required(allowed_roles=['admin'])
def stock_list(request):
    stocks = StoreStock.objects.select_related('branch', 'plant').all()
    return render(request, 'admin/stock/list.html', {'stocks': stocks})

@role_required(allowed_roles=['admin'])
def stock_update(request, pk):
    stock = get_object_or_404(StoreStock, pk=pk)
    if request.method == 'POST':
        new_qty = request.POST.get('quantity')
        stock.quantity = new_qty
        stock.save()
        return redirect('admin_stock_list')
    return render(request, 'admin/stock/form.html', {'stock': stock})