from datetime import timedelta

from django.db.models import Count, Q, Sum
from django.utils import timezone

from account.models import AuditLog, User

from .models import Branch, Package, PackageStatus, Vehicle

REPORT_CATEGORIES = {
    'operational': 'Operational Reports',
    'financial': 'Financial Reports',
    'activity': 'User Activity Reports',
}

REPORT_DEFINITIONS = {
    'packages_sent_per_branch': {
        'title': 'Packages Sent Per Branch',
        'category': 'operational',
        'description': 'Count of packages dispatched from each branch.',
    },
    'packages_received_per_branch': {
        'title': 'Packages Received Per Branch',
        'category': 'operational',
        'description': 'Count of packages arriving at each destination branch.',
    },
    'packages_delivered': {
        'title': 'Packages Delivered',
        'category': 'operational',
        'description': 'All delivered packages within the selected date range.',
    },
    'packages_in_transit': {
        'title': 'Packages In Transit',
        'category': 'operational',
        'description': 'Packages currently on the road.',
    },
    'delayed_packages': {
        'title': 'Delayed Packages',
        'category': 'operational',
        'description': 'Packages in transit for more than 3 days or pending dispatch over 2 days.',
    },
    'vehicle_utilization': {
        'title': 'Vehicle Utilization',
        'category': 'operational',
        'description': 'Shipments assigned per vehicle and fleet status.',
    },
    'revenue_by_branch': {
        'title': 'Revenue by Branch',
        'category': 'financial',
        'description': 'Total transport fees collected per origin branch.',
    },
    'revenue_by_date': {
        'title': 'Revenue by Date Range',
        'category': 'financial',
        'description': 'Daily revenue totals for the selected period.',
    },
    'revenue_by_vehicle': {
        'title': 'Revenue by Vehicle',
        'category': 'financial',
        'description': 'Transport fees generated per assigned vehicle.',
    },
    'revenue_by_user': {
        'title': 'Revenue by User',
        'category': 'financial',
        'description': 'Transport fees from packages registered by each user.',
    },
    'packages_registered_by_user': {
        'title': 'Packages Registered by User',
        'category': 'activity',
        'description': 'Number of packages registered by each staff member.',
    },
    'packages_received_by_user': {
        'title': 'Packages Received by User',
        'category': 'activity',
        'description': 'Arrival confirmations performed by each officer.',
    },
    'login_activity': {
        'title': 'Login Activity',
        'category': 'activity',
        'description': 'User login and logout audit trail.',
    },
}


def _parse_dates(date_from, date_to):
    today = timezone.localdate()
    start = date_from or (today - timedelta(days=30))
    end = date_to or today
    return start, end


def _filter_packages_by_date(qs, date_from, date_to, field='registered_at'):
    start, end = _parse_dates(date_from, date_to)
    return qs.filter(**{f'{field}__date__gte': start, f'{field}__date__lte': end})


def get_reports_by_category():
    grouped = {key: [] for key in REPORT_CATEGORIES}
    for slug, meta in REPORT_DEFINITIONS.items():
        grouped[meta['category']].append({'slug': slug, **meta})
    return grouped


def generate_report(slug, date_from=None, date_to=None):
    if slug not in REPORT_DEFINITIONS:
        raise ValueError(f'Unknown report: {slug}')

    meta = REPORT_DEFINITIONS[slug]
    generators = {
        'packages_sent_per_branch': _packages_sent_per_branch,
        'packages_received_per_branch': _packages_received_per_branch,
        'packages_delivered': _packages_delivered,
        'packages_in_transit': _packages_in_transit,
        'delayed_packages': _delayed_packages,
        'vehicle_utilization': _vehicle_utilization,
        'revenue_by_branch': _revenue_by_branch,
        'revenue_by_date': _revenue_by_date,
        'revenue_by_vehicle': _revenue_by_vehicle,
        'revenue_by_user': _revenue_by_user,
        'packages_registered_by_user': _packages_registered_by_user,
        'packages_received_by_user': _packages_received_by_user,
        'login_activity': _login_activity,
    }

    headers, rows, summary = generators[slug](date_from, date_to)
    start, end = _parse_dates(date_from, date_to)

    return {
        'slug': slug,
        'title': meta['title'],
        'description': meta['description'],
        'category': meta['category'],
        'headers': headers,
        'rows': rows,
        'summary': summary,
        'date_from': start,
        'date_to': end,
    }


def _packages_sent_per_branch(date_from, date_to):
    qs = _filter_packages_by_date(Package.objects.all(), date_from, date_to)
    data = (
        qs.values('origin_branch__code', 'origin_branch__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    rows = [[r['origin_branch__code'], r['origin_branch__name'], r['count']] for r in data]
    total = sum(r[2] for r in rows)
    return ['Branch Code', 'Branch Name', 'Packages Sent'], rows, {'Total Sent': total}


def _packages_received_per_branch(date_from, date_to):
    qs = _filter_packages_by_date(Package.objects.all(), date_from, date_to)
    data = (
        qs.values('destination_branch__code', 'destination_branch__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    rows = [[r['destination_branch__code'], r['destination_branch__name'], r['count']] for r in data]
    total = sum(r[2] for r in rows)
    return ['Branch Code', 'Branch Name', 'Packages Received'], rows, {'Total Received': total}


def _packages_delivered(date_from, date_to):
    start, end = _parse_dates(date_from, date_to)
    qs = Package.objects.filter(
        status=PackageStatus.DELIVERED,
        delivered_at__date__gte=start,
        delivered_at__date__lte=end,
    ).select_related('origin_branch', 'destination_branch')
    rows = [
        [
            p.tracking_number,
            p.origin_branch.code,
            p.destination_branch.code,
            p.delivered_at.strftime('%Y-%m-%d %H:%M') if p.delivered_at else '',
            f'{p.transport_fee:.2f}',
        ]
        for p in qs
    ]
    total = qs.aggregate(total=Sum('transport_fee'))['total'] or 0
    return (
        ['Tracking #', 'Origin', 'Destination', 'Delivered At', 'Fee'],
        rows,
        {'Total Delivered': len(rows), 'Total Revenue': f'{total:.2f}'},
    )


def _packages_in_transit(date_from, date_to):
    qs = Package.objects.filter(status=PackageStatus.IN_TRANSIT).select_related(
        'origin_branch', 'destination_branch', 'assigned_vehicle',
    )
    rows = [
        [
            p.tracking_number,
            p.origin_branch.code,
            p.destination_branch.code,
            p.assigned_vehicle.plate_number if p.assigned_vehicle else '—',
            p.registered_at.strftime('%Y-%m-%d'),
        ]
        for p in qs
    ]
    return ['Tracking #', 'Origin', 'Destination', 'Vehicle', 'Registered'], rows, {'In Transit': len(rows)}


def _delayed_packages(date_from, date_to):
    now = timezone.now()
    transit_cutoff = now - timedelta(days=3)
    dispatch_cutoff = now - timedelta(days=2)

    qs = Package.objects.filter(
        Q(status=PackageStatus.IN_TRANSIT, registered_at__lte=transit_cutoff)
        | Q(status=PackageStatus.READY_FOR_DISPATCH, registered_at__lte=dispatch_cutoff)
    ).select_related('origin_branch', 'destination_branch')

    rows = [
        [
            p.tracking_number,
            p.get_status_display(),
            p.origin_branch.code,
            p.destination_branch.code,
            p.registered_at.strftime('%Y-%m-%d'),
            (now - p.registered_at).days,
        ]
        for p in qs
    ]
    return ['Tracking #', 'Status', 'Origin', 'Destination', 'Registered', 'Days Elapsed'], rows, {'Delayed': len(rows)}


def _vehicle_utilization(date_from, date_to):
    qs = _filter_packages_by_date(
        Package.objects.exclude(assigned_vehicle__isnull=True),
        date_from,
        date_to,
    )
    data = (
        qs.values('assigned_vehicle__plate_number', 'assigned_vehicle__driver_name', 'assigned_vehicle__status')
        .annotate(shipments=Count('id'), revenue=Sum('transport_fee'))
        .order_by('-shipments')
    )
    rows = [
        [
            r['assigned_vehicle__plate_number'],
            r['assigned_vehicle__driver_name'],
            r['assigned_vehicle__status'],
            r['shipments'],
            f"{r['revenue'] or 0:.2f}",
        ]
        for r in data
    ]
    idle = Vehicle.objects.annotate(shipment_count=Count('shipments')).filter(shipment_count=0).count()
    return ['Plate', 'Driver', 'Status', 'Shipments', 'Revenue'], rows, {'Vehicles Used': len(rows), 'Idle Vehicles': idle}


def _revenue_by_branch(date_from, date_to):
    qs = _filter_packages_by_date(Package.objects.all(), date_from, date_to)
    data = (
        qs.values('origin_branch__code', 'origin_branch__name')
        .annotate(revenue=Sum('transport_fee'), packages=Count('id'))
        .order_by('-revenue')
    )
    rows = [
        [r['origin_branch__code'], r['origin_branch__name'], r['packages'], f"{r['revenue'] or 0:.2f}"]
        for r in data
    ]
    total = sum(float(r[3]) for r in rows)
    return ['Branch Code', 'Branch Name', 'Packages', 'Revenue'], rows, {'Total Revenue': f'{total:.2f}'}


def _revenue_by_date(date_from, date_to):
    start, end = _parse_dates(date_from, date_to)
    qs = Package.objects.filter(
        registered_at__date__gte=start,
        registered_at__date__lte=end,
    )
    from django.db.models.functions import TruncDate
    data = (
        qs.annotate(day=TruncDate('registered_at'))
        .values('day')
        .annotate(packages=Count('id'), revenue=Sum('transport_fee'))
        .order_by('day')
    )
    rows = [
        [r['day'].strftime('%Y-%m-%d'), r['packages'], f"{r['revenue'] or 0:.2f}"]
        for r in data
    ]
    total = qs.aggregate(total=Sum('transport_fee'))['total'] or 0
    return ['Date', 'Packages', 'Revenue'], rows, {'Total Revenue': f'{total:.2f}'}


def _revenue_by_vehicle(date_from, date_to):
    qs = _filter_packages_by_date(
        Package.objects.exclude(assigned_vehicle__isnull=True),
        date_from,
        date_to,
    )
    data = (
        qs.values('assigned_vehicle__plate_number', 'assigned_vehicle__vehicle_type')
        .annotate(revenue=Sum('transport_fee'), packages=Count('id'))
        .order_by('-revenue')
    )
    rows = [
        [r['assigned_vehicle__plate_number'], r['assigned_vehicle__vehicle_type'], r['packages'], f"{r['revenue'] or 0:.2f}"]
        for r in data
    ]
    total = sum(float(r[3]) for r in rows)
    return ['Plate', 'Type', 'Packages', 'Revenue'], rows, {'Total Revenue': f'{total:.2f}'}


def _revenue_by_user(date_from, date_to):
    qs = _filter_packages_by_date(Package.objects.all(), date_from, date_to)
    data = (
        qs.values('registered_by__username', 'registered_by__full_name')
        .annotate(revenue=Sum('transport_fee'), packages=Count('id'))
        .order_by('-revenue')
    )
    rows = [
        [r['registered_by__username'], r['registered_by__full_name'], r['packages'], f"{r['revenue'] or 0:.2f}"]
        for r in data
    ]
    total = sum(float(r[3]) for r in rows)
    return ['Username', 'Full Name', 'Packages', 'Revenue'], rows, {'Total Revenue': f'{total:.2f}'}


def _packages_registered_by_user(date_from, date_to):
    qs = _filter_packages_by_date(Package.objects.all(), date_from, date_to)
    data = (
        qs.values('registered_by__username', 'registered_by__full_name', 'registered_by__branch__code')
        .annotate(packages=Count('id'))
        .order_by('-packages')
    )
    rows = [[r['registered_by__username'], r['registered_by__full_name'], r['registered_by__branch__code'] or '—', r['packages']] for r in data]
    total = sum(r[3] for r in rows)
    return ['Username', 'Full Name', 'Branch', 'Packages Registered'], rows, {'Total': total}


def _packages_received_by_user(date_from, date_to):
    start, end = _parse_dates(date_from, date_to)
    qs = Package.objects.filter(
        received_by__isnull=False,
        arrived_at__date__gte=start,
        arrived_at__date__lte=end,
    )
    data = (
        qs.values('received_by__username', 'received_by__full_name', 'received_at_branch__code')
        .annotate(packages=Count('id'))
        .order_by('-packages')
    )
    rows = [[r['received_by__username'], r['received_by__full_name'], r['received_at_branch__code'] or '—', r['packages']] for r in data]
    total = sum(r[3] for r in rows)
    return ['Username', 'Full Name', 'Branch', 'Packages Received'], rows, {'Total': total}


def _login_activity(date_from, date_to):
    start, end = _parse_dates(date_from, date_to)
    qs = AuditLog.objects.filter(
        action__in=[AuditLog.Action.LOGIN, AuditLog.Action.LOGOUT],
        timestamp__date__gte=start,
        timestamp__date__lte=end,
    ).select_related('user').order_by('-timestamp')[:500]
    rows = [
        [
            log.timestamp.strftime('%Y-%m-%d %H:%M'),
            log.user.username if log.user else '—',
            log.user.full_name if log.user else '—',
            log.get_action_display(),
            log.ip_address or '—',
        ]
        for log in qs
    ]
    return ['Timestamp', 'Username', 'Full Name', 'Action', 'IP Address'], rows, {'Records': len(rows)}
