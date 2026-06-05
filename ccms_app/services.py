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


def normalize_phone(phone):
    return ''.join(char for char in (phone or '') if char.isdigit())


def get_package_by_tracking(tracking_number):
    if not tracking_number:
        return None
    return (
        Package.objects
        .select_related('origin_branch', 'destination_branch', 'registered_by')
        .filter(tracking_number__iexact=tracking_number.strip())
        .first()
    )


def can_confirm_arrival(user, package):
    if not package:
        return False, 'Package not found.'
    if package.status in (PackageStatus.DELIVERED, PackageStatus.CANCELLED, PackageStatus.ARRIVED):
        return False, f'Package is already {package.get_status_display().lower()}.'
    if package.status not in (PackageStatus.IN_TRANSIT, PackageStatus.READY_FOR_DISPATCH):
        return False, 'Package must be in transit or ready for dispatch before arrival confirmation.'
    if user.is_branch_officer:
        if not user.branch_id:
            return False, 'Your account has no assigned branch.'
        if package.destination_branch_id != user.branch_id:
            return False, 'This package is not destined for your branch.'
    return True, ''


def confirm_arrival(package, user):
    receiving_branch = user.branch if user.is_branch_officer else package.destination_branch
    now = timezone.now()

    record_status_change(
        package,
        PackageStatus.ARRIVED,
        user,
        notes=f'Arrival confirmed at {receiving_branch.code}.',
    )
    package.received_by = user
    package.received_at_branch = receiving_branch
    package.arrived_at = now
    package.save(update_fields=['received_by', 'received_at_branch', 'arrived_at', 'updated_at'])
    return package


def can_confirm_delivery(user, package):
    if not package:
        return False, 'Package not found.'
    if package.status == PackageStatus.DELIVERED:
        return False, 'Package has already been delivered.'
    if package.status not in (PackageStatus.ARRIVED, PackageStatus.READY_FOR_PICKUP):
        return False, 'Package must arrive at the destination branch before delivery.'
    if user.is_branch_officer:
        if not user.branch_id:
            return False, 'Your account has no assigned branch.'
        if package.destination_branch_id != user.branch_id:
            return False, 'This package cannot be delivered from your branch.'
    return True, ''


def verify_receiver(package, receiver_id, receiver_name, receiver_phone):
    id_match = package.receiver_id_number.strip().lower() == receiver_id.strip().lower()
    name_match = package.receiver_full_name.strip().lower() == receiver_name.strip().lower()
    phone_match = normalize_phone(package.receiver_phone) == normalize_phone(receiver_phone)
    return id_match and name_match and phone_match


def confirm_delivery(package, user, receiver_id_number):
    now = timezone.now()
    record_status_change(
        package,
        PackageStatus.DELIVERED,
        user,
        notes='Package collected by receiver.',
    )
    package.delivered_by = user
    package.delivered_at = now
    package.delivery_receiver_id_number = receiver_id_number
    package.save(update_fields=['delivered_by', 'delivered_at', 'delivery_receiver_id_number', 'updated_at'])
    return package
