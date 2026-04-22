from django.shortcuts import render, get_object_or_404, redirect

from ..decorators import role_required
from ..model.plant import Plant
from admin_forms import PlantForm

@role_required(allowed_roles=['admin'])
def plant_list(request):
    items = Plant.objects.select_related('category').all()
    return render(request, 'admin/plant/list.html', {'items': items})

@role_required(allowed_roles=['admin'])
def plant_upsert(request, pk=None):
    obj = get_object_or_404(Plant, pk=pk) if pk else None
    form = PlantForm(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('admin_plant_list')
    return render(request, 'admin/plant/form.html', {'form': form})

@role_required(allowed_roles=['admin'])
def plant_delete(request, pk):
    get_object_or_404(Plant, pk=pk).delete()
    return redirect('admin_plant_list')
