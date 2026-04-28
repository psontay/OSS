from django.shortcuts import render, get_object_or_404, redirect
from ..models.category import Category
from admin_forms import CategoryForm
from GISDjango.decorators import role_required

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
