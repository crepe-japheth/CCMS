from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from account.decorators import admin_required
from account.models import AuditLog
from account.utils import log_audit

from .forms import BranchForm, VehicleForm
from .models import Branch, Package, Vehicle


@admin_required
def branch_list(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')

    branches = Branch.objects.all()
    if query:
        branches = branches.filter(
            Q(name__icontains=query) | Q(code__icontains=query) | Q(location__icontains=query)
        )
    if status == 'active':
        branches = branches.filter(is_active=True)
    elif status == 'inactive':
        branches = branches.filter(is_active=False)

    return render(request, 'ccms_app/branches/list.html', {
        'active_nav': 'branches',
        'branches': branches,
        'query': query,
        'status_filter': status,
    })


@admin_required
def branch_create(request):
    form = BranchForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        branch = form.save()
        log_audit(
            request.user,
            AuditLog.Action.BRANCH_CREATED,
            description=f'Created branch {branch.code}.',
            request=request,
        )
        messages.success(request, f'Branch "{branch.name}" created successfully.')
        return redirect('ccms_app:branch_list')

    return render(request, 'ccms_app/branches/form.html', {
        'active_nav': 'branches',
        'form': form,
        'title': 'Add Branch',
        'submit_label': 'Create Branch',
    })


@admin_required
def branch_edit(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    form = BranchForm(request.POST or None, instance=branch)
    if request.method == 'POST' and form.is_valid():
        branch = form.save()
        log_audit(
            request.user,
            AuditLog.Action.BRANCH_UPDATED,
            description=f'Updated branch {branch.code}.',
            request=request,
        )
        messages.success(request, f'Branch "{branch.name}" updated successfully.')
        return redirect('ccms_app:branch_list')

    return render(request, 'ccms_app/branches/form.html', {
        'active_nav': 'branches',
        'form': form,
        'title': 'Edit Branch',
        'submit_label': 'Save Changes',
        'object': branch,
    })


@admin_required
def branch_toggle_status(request, pk):
    if request.method != 'POST':
        return redirect('ccms_app:branch_list')

    branch = get_object_or_404(Branch, pk=pk)
    branch.is_active = not branch.is_active
    branch.save(update_fields=['is_active', 'updated_at'])

    state = 'activated' if branch.is_active else 'deactivated'
    log_audit(
        request.user,
        AuditLog.Action.BRANCH_UPDATED,
        description=f'Branch {branch.code} {state}.',
        request=request,
    )
    messages.success(request, f'Branch "{branch.name}" has been {state}.')
    return redirect('ccms_app:branch_list')


@admin_required
def vehicle_list(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')

    vehicles = Vehicle.objects.all()
    if query:
        vehicles = vehicles.filter(
            Q(plate_number__icontains=query)
            | Q(driver_name__icontains=query)
            | Q(vehicle_type__icontains=query)
        )
    if status:
        vehicles = vehicles.filter(status=status)

    return render(request, 'ccms_app/vehicles/list.html', {
        'active_nav': 'vehicles',
        'vehicles': vehicles,
        'query': query,
        'status_filter': status,
    })


@admin_required
def vehicle_create(request):
    form = VehicleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        vehicle = form.save()
        log_audit(
            request.user,
            AuditLog.Action.VEHICLE_ASSIGNED,
            description=f'Registered vehicle {vehicle.plate_number}.',
            request=request,
        )
        messages.success(request, f'Vehicle "{vehicle.plate_number}" registered successfully.')
        return redirect('ccms_app:vehicle_list')

    return render(request, 'ccms_app/vehicles/form.html', {
        'active_nav': 'vehicles',
        'form': form,
        'title': 'Register Vehicle',
        'submit_label': 'Register Vehicle',
    })


@admin_required
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    form = VehicleForm(request.POST or None, instance=vehicle)
    if request.method == 'POST' and form.is_valid():
        vehicle = form.save()
        log_audit(
            request.user,
            AuditLog.Action.VEHICLE_ASSIGNED,
            description=f'Updated vehicle {vehicle.plate_number}.',
            request=request,
        )
        messages.success(request, f'Vehicle "{vehicle.plate_number}" updated successfully.')
        return redirect('ccms_app:vehicle_list')

    return render(request, 'ccms_app/vehicles/form.html', {
        'active_nav': 'vehicles',
        'form': form,
        'title': 'Edit Vehicle',
        'submit_label': 'Save Changes',
        'object': vehicle,
    })


@admin_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    shipments = (
        Package.objects
        .filter(assigned_vehicle=vehicle)
        .select_related('origin_branch', 'destination_branch')
        .order_by('-registered_at')
    )
    return render(request, 'ccms_app/vehicles/detail.html', {
        'active_nav': 'vehicles',
        'vehicle': vehicle,
        'shipments': shipments,
    })
