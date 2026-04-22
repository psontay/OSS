from ..decorators import role_required
from ..model.user import User
from django.shortcuts import render, get_object_or_404, redirect

@role_required(allowed_roles=['admin'])
def user_list(request):
    items = User.objects.all()
    return render(request, 'admin/user/list.html', {'items': items})

@role_required(allowed_roles=['admin'])
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if not user.is_superuser:
        user.delete()
    return redirect('admin_user_list')