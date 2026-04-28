from django.shortcuts import render, get_object_or_404, redirect
from OSS.models.category import Category  # Đổi từ ..models thành đường dẫn tuyệt đối cho chắc
from OSS.models.forms import CategoryForm  # Kiểm tra lại tên file chứa CategoryForm của ông
from OSS.decorators import role_required   # BẮT QUẢ TANG: Đổi GISDjango thành OSS

@role_required(allowed_roles=['admin'])
def category_list(request):
    items = Category.objects.all()
    return render(request, 'admin/category/list.html', {'items': items})

@role_required(allowed_roles=['admin'])
def category_upsert(request, pk=None): # Upsert = Update or Insert
    obj = get_object_or_404(Category, pk=pk) if pk else None
    form = CategoryForm(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('admin_category_list')
    return render(request, 'admin/category/form.html', {'form': form, 'is_edit': pk})

@role_required(allowed_roles=['admin'])
def category_delete(request, pk):
    get_object_or_404(Category, pk=pk).delete()
    return redirect('admin_category_list')