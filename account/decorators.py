from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import UserRole


def role_required(*roles):
    """Restrict a view to users with one of the given roles."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                messages.error(request, 'You do not have permission to access that page.')
                return redirect('ccms_app:dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


admin_required = role_required(UserRole.ADMIN_MANAGER)
branch_officer_required = role_required(UserRole.BRANCH_OFFICER)
