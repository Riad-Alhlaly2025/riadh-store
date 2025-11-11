from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def check_user_role(role):
    """
    Decorator to check if the user has a specific role
    """
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, 'userprofile') and request.user.userprofile.role == role:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'ليس لديك الصلاحية للوصول إلى هذه الصفحة.')
                return redirect('home')
        return _wrapped_view
    return decorator

def manager_required(view_func):
    """
    Decorator to require manager role
    """
    return check_user_role('manager')(view_func)

def seller_required(view_func):
    """
    Decorator to require seller role
    """
    return check_user_role('seller')(view_func)

def buyer_required(view_func):
    """
    Decorator to require buyer role
    """
    return check_user_role('buyer')(view_func)