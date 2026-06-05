from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import Package, PackageStatus, PackageStatusHistory


def packages_for_user(user):
    """Return packages visible to the given user based on role."""
    qs = Package.objects.select_related(
        'origin_branch', 'destination_branch', 'registered_by', 'assigned_vehicle',
    )
    if user.is_branch_officer and user.branch_id:
        return qs.filter(
            Q(origin_branch=user.branch) | Q(destination_branch=user.branch)
        )
    return qs


def get_package_for_user(user, pk):
    return packages_for_user(user).filter(pk=pk).first()


def generate_tracking_number():
    """Generate unique tracking number: CCMS-YYYYMMDD-000001."""
    today = timezone.localdate().strftime('%Y%m%d')
    prefix = f'CCMS-{today}-'

    with transaction.atomic():
        last_package = (
            Package.objects
            .select_for_update()
            .filter(tracking_number__startswith=prefix)
            .order_by('-tracking_number')
            .first()
        )
        if last_package:
            sequence = int(last_package.tracking_number.rsplit('-', 1)[-1]) + 1
        else:
            sequence = 1

    return f'{prefix}{sequence:06d}'


def record_status_change(package, new_status, user=None, notes=''):
    """Update package status and append to history."""
    if package.status == new_status:
        return package

    PackageStatusHistory.objects.create(
        package=package,
        status=new_status,
        changed_by=user,
        notes=notes,
    )
    package.status = new_status
    package.save(update_fields=['status', 'updated_at'])
    return package


def create_package_with_status(package, user=None):
    """Save a new package; initial status history is created via signal."""
    if user and not package.registered_by_id:
        package.registered_by = user
    package.save()
    return package
