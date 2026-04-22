from GISDjango.controller.admin_forms import BranchForm
from GISDjango.decorators import role_required
from GISDjango.models import StoreBranch
from django.shortcuts import render, get_object_or_404, redirect


@role_required(allowed_roles=['admin'])
def branch_list(request):
    items = StoreBranch.objects.all()
    return render(request, 'admin/branch/list.html', {'items': items})

@role_required(allowed_roles=['admin'])
def branch_upsert(request, pk=None):
    obj = get_object_or_404(StoreBranch, pk=pk) if pk else None
    form = BranchForm(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('admin_branch_list')
    return render(request, 'admin/branch/form.html', {'form': form})