from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from account.models import AuditLog
from account.utils import log_audit

from .forms import DeliveryVerificationForm, PackageStatusUpdateForm, TrackingLookupForm
from .services import (
    apply_manual_status_change,
    can_confirm_arrival,
    can_confirm_delivery,
    confirm_arrival,
    confirm_delivery,
    get_package_by_tracking,
    packages_for_user,
    verify_receiver,
)


@login_required
def scan_arrival(request):
    if request.user.is_branch_officer and not request.user.branch_id:
        messages.error(request, 'Your account has no assigned branch. Contact an administrator.')
        return redirect('ccms_app:dashboard')

    form = TrackingLookupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        tracking = form.cleaned_data['tracking_number']
        return redirect('ccms_app:arrival_confirm', tracking_number=tracking)

    return render(request, 'ccms_app/operations/scan_arrival.html', {
        'active_nav': 'scan_arrival',
        'form': form,
    })


@login_required
def arrival_confirm(request, tracking_number):
    package = get_package_by_tracking(tracking_number)
    allowed, error = can_confirm_arrival(request.user, package)

    if not package:
        messages.error(request, 'No package found with that tracking number.')
        return redirect('ccms_app:scan_arrival')

    if request.method == 'POST':
        if not allowed:
            messages.error(request, error)
            return redirect('ccms_app:scan_arrival')

        confirm_arrival(package, request.user)
        log_audit(
            request.user,
            AuditLog.Action.PACKAGE_ARRIVAL,
            description=f'Confirmed arrival of {package.tracking_number}.',
            request=request,
        )
        messages.success(request, f'Arrival confirmed for {package.tracking_number}.')
        return redirect('ccms_app:package_detail', pk=package.pk)

    return render(request, 'ccms_app/operations/arrival_confirm.html', {
        'active_nav': 'scan_arrival',
        'package': package,
        'can_confirm': allowed,
        'error_message': error,
    })


@login_required
def confirm_delivery_lookup(request):
    if request.user.is_branch_officer and not request.user.branch_id:
        messages.error(request, 'Your account has no assigned branch. Contact an administrator.')
        return redirect('ccms_app:dashboard')

    form = TrackingLookupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        tracking = form.cleaned_data['tracking_number']
        return redirect('ccms_app:delivery_confirm', tracking_number=tracking)

    return render(request, 'ccms_app/operations/delivery_lookup.html', {
        'active_nav': 'confirm_delivery',
        'form': form,
    })


@login_required
def delivery_confirm(request, tracking_number):
    package = get_package_by_tracking(tracking_number)
    allowed, error = can_confirm_delivery(request.user, package)

    if not package:
        messages.error(request, 'No package found with that tracking number.')
        return redirect('ccms_app:confirm_delivery_lookup')

    form = DeliveryVerificationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        if not allowed:
            messages.error(request, error)
            return redirect('ccms_app:confirm_delivery_lookup')

        data = form.cleaned_data
        if not verify_receiver(
            package,
            data['receiver_id_number'],
            data['receiver_full_name'],
            data['receiver_phone'],
        ):
            messages.error(
                request,
                'Receiver details do not match our records. Verify ID, name, and phone number.',
            )
        else:
            confirm_delivery(package, request.user, data['receiver_id_number'])
            log_audit(
                request.user,
                AuditLog.Action.PACKAGE_DELIVERED,
                description=f'Confirmed delivery of {package.tracking_number}.',
                request=request,
            )
            messages.success(request, f'Package {package.tracking_number} marked as delivered.')
            return redirect('ccms_app:package_detail', pk=package.pk)

    return render(request, 'ccms_app/operations/delivery_confirm.html', {
        'active_nav': 'confirm_delivery',
        'package': package,
        'form': form,
        'can_confirm': allowed,
        'error_message': error,
    })


@login_required
def update_status_lookup(request):
    form = TrackingLookupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        tracking = form.cleaned_data['tracking_number']
        return redirect('ccms_app:update_status', tracking_number=tracking)

    return render(request, 'ccms_app/operations/update_status_lookup.html', {
        'active_nav': 'update_status',
        'form': form,
    })


@login_required
def update_status(request, tracking_number):
    package = packages_for_user(request.user).filter(
        tracking_number__iexact=tracking_number.strip()
    ).first()

    if not package:
        messages.error(request, 'Package not found or you do not have access.')
        return redirect('ccms_app:update_status_lookup')

    form = PackageStatusUpdateForm(request.POST or None, package=package)
    if request.method == 'POST' and form.is_valid():
        new_status = form.cleaned_data['status']
        notes = form.cleaned_data['notes']
        package, changed = apply_manual_status_change(package, new_status, request.user, notes=notes)
        if changed:
            log_audit(
                request.user,
                AuditLog.Action.PACKAGE_STATUS_CHANGED,
                description=f'Status of {package.tracking_number} changed to {package.status_label}.',
                request=request,
            )
            messages.success(request, f'Status updated to {package.status_label}.')
            return redirect('ccms_app:package_detail', pk=package.pk)
        messages.info(request, 'Status is already set to that value.')

    return render(request, 'ccms_app/operations/update_status.html', {
        'active_nav': 'update_status',
        'package': package,
        'form': form,
    })


def track_shipment(request):
    """Public shipment tracking — no login required."""
    form = TrackingLookupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        tracking = form.cleaned_data['tracking_number']
        return redirect('ccms_app:track_result', tracking_number=tracking)

    return render(request, 'ccms_app/track/lookup.html', {
        'form': form,
    })


def track_result(request, tracking_number):
    """Public tracking result page."""
    package = get_package_by_tracking(tracking_number)
    history = []
    if package:
        history = package.status_history.select_related('changed_by').all()[:10]

    return render(request, 'ccms_app/track/result.html', {
        'package': package,
        'tracking_number': tracking_number,
        'history': history,
    })
