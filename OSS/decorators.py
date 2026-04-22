from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles=[]):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            messages.error(request, f"Khu vực này chỉ dành cho {', '.join(allowed_roles)}!")
            return redirect('home')
        return _wrapped_view
    return decorator