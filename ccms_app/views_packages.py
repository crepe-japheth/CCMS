from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render

from account.models import AuditLog
from account.utils import log_audit

from .forms import PackageRegistrationForm, PackageStatusUpdateForm
from .models import PackageStatus
from .qr_utils import generate_qr_png
from .services import apply_manual_status_change, create_package_with_status, packages_for_user


@login_required
def package_list(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')

    packages = packages_for_user(request.user)
    if query:
        packages = packages.filter(
            Q(tracking_number__icontains=query)
            | Q(sender_full_name__icontains=query)
            | Q(receiver_full_name__icontains=query)
            | Q(sender_phone__icontains=query)
            | Q(receiver_phone__icontains=query)
        )
    if status:
        packages = packages.filter(status=status)

    return render(request, 'ccms_app/packages/list.html', {
        'active_nav': 'packages',
        'packages': packages,
        'query': query,
        'status_filter': status,
    })


@login_required
def package_register(request):
    if request.user.is_branch_officer and not request.user.branch_id:
        messages.error(request, 'Your account has no assigned branch. Contact an administrator.')
        return redirect('ccms_app:dashboard')

    form = PackageRegistrationForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        package = form.save(commit=False)
        package.registered_by = request.user
        package.status = PackageStatus.REGISTERED

        if request.user.is_branch_officer:
            package.origin_branch = request.user.branch

        create_package_with_status(package, user=request.user)

        log_audit(
            request.user,
            AuditLog.Action.PACKAGE_REGISTERED,
            description=f'Registered package {package.tracking_number}.',
            request=request,
        )
        messages.success(
            request,
            f'Package {package.tracking_number} registered successfully. Print the QR label and attach it to the package.',
        )
        return redirect('ccms_app:package_qr', pk=package.pk)

    return render(request, 'ccms_app/packages/register.html', {
        'active_nav': 'register_package',
        'form': form,
    })


@login_required
def package_detail(request, pk):
    package = packages_for_user(request.user).filter(pk=pk).first()
    if not package:
        raise Http404('Package not found.')

    status_form = PackageStatusUpdateForm(request.POST or None, package=package)
    if request.method == 'POST' and 'update_status' in request.POST and status_form.is_valid():
        new_status = status_form.cleaned_data['status']
        notes = status_form.cleaned_data['notes']
        package, changed = apply_manual_status_change(package, new_status, request.user, notes=notes)
        if changed:
            log_audit(
                request.user,
                AuditLog.Action.PACKAGE_STATUS_CHANGED,
                description=f'Status of {package.tracking_number} changed to {package.status_label}.',
                request=request,
            )
            messages.success(request, f'Status updated to {package.status_label}.')
        else:
            messages.info(request, 'Status is already set to that value.')
        return redirect('ccms_app:package_detail', pk=package.pk)

    history = package.status_history.select_related('changed_by').all()
    return render(request, 'ccms_app/packages/detail.html', {
        'active_nav': 'packages',
        'package': package,
        'history': history,
        'status_form': status_form,
    })


@login_required
def package_qr(request, pk):
    package = packages_for_user(request.user).filter(pk=pk).first()
    if not package:
        raise Http404('Package not found.')

    return render(request, 'ccms_app/packages/qr_label.html', {
        'package': package,
    })


@login_required
def package_qr_image(request, pk):
    package = packages_for_user(request.user).filter(pk=pk).first()
    if not package:
        raise Http404('Package not found.')

    png = generate_qr_png(package.tracking_number)
    return HttpResponse(png, content_type='image/png')
