from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import admin_required
from .forms import UserCreateForm, UserUpdateForm
from .models import AuditLog, User, UserStatus
from .utils import log_audit


@admin_required
def user_list(request):
    query = request.GET.get('q', '').strip()
    role = request.GET.get('role', '')
    status = request.GET.get('status', '')

    users = User.objects.select_related('branch').all()
    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(full_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone_number__icontains=query)
        )
    if role:
        users = users.filter(role=role)
    if status:
        users = users.filter(status=status)

    return render(request, 'account/users/list.html', {
        'active_nav': 'users',
        'users': users,
        'query': query,
        'role_filter': role,
        'status_filter': status,
    })


@admin_required
def user_create(request):
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        log_audit(
            request.user,
            AuditLog.Action.USER_CREATED,
            description=f'Created user {user.username} ({user.get_role_display()}).',
            request=request,
        )
        messages.success(request, f'User "{user.full_name}" created successfully.')
        return redirect('account:user_list')

    return render(request, 'account/users/form.html', {
        'active_nav': 'users',
        'form': form,
        'title': 'Add User',
        'submit_label': 'Create User',
    })


@admin_required
def user_edit(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    form = UserUpdateForm(request.POST or None, instance=user_obj)
    if request.method == 'POST' and form.is_valid():
        user_obj = form.save()
        log_audit(
            request.user,
            AuditLog.Action.USER_UPDATED,
            description=f'Updated user {user_obj.username}.',
            request=request,
        )
        messages.success(request, f'User "{user_obj.full_name}" updated successfully.')
        return redirect('account:user_list')

    return render(request, 'account/users/form.html', {
        'active_nav': 'users',
        'form': form,
        'title': 'Edit User',
        'submit_label': 'Save Changes',
        'object': user_obj,
    })


@admin_required
def user_toggle_status(request, pk):
    if request.method != 'POST':
        return redirect('account:user_list')

    user_obj = get_object_or_404(User, pk=pk)
    if user_obj == request.user:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('account:user_list')

    user_obj.status = (
        UserStatus.INACTIVE if user_obj.status == UserStatus.ACTIVE else UserStatus.ACTIVE
    )
    user_obj.save(update_fields=['status'])

    state = 'activated' if user_obj.status == UserStatus.ACTIVE else 'deactivated'
    log_audit(
        request.user,
        AuditLog.Action.USER_UPDATED,
        description=f'User {user_obj.username} {state}.',
        request=request,
    )
    messages.success(request, f'User "{user_obj.full_name}" has been {state}.')
    return redirect('account:user_list')
