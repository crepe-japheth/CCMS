import json
from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import Branch, Package, PackageStatus, Vehicle, VehicleStatus
from .services import packages_for_user

PERIOD_CHOICES = {
    'month': 'This Month',
    'last_month': 'Last Month',
    'year': 'This Year',
    'all': 'All Time',
}

STATUS_CHART_CONFIG = [
    (PackageStatus.REGISTERED, 'Registered', '#3b82f6'),
    (PackageStatus.READY_FOR_DISPATCH, 'Ready for Dispatch', '#6366f1'),
    (PackageStatus.IN_TRANSIT, 'In Transit', '#8b5cf6'),
    (PackageStatus.ARRIVED, 'Arrived', '#f59e0b'),
    (PackageStatus.READY_FOR_PICKUP, 'Ready for Pickup', '#f97316'),
    (PackageStatus.DELIVERED, 'Delivered', '#10b981'),
    (PackageStatus.CANCELLED, 'Cancelled', '#ef4444'),
]


def _period_bounds(period):
    today = timezone.localdate()
    if period == 'month':
        start = today.replace(day=1)
        end = today
    elif period == 'last_month':
        first_this_month = today.replace(day=1)
        end = first_this_month - timedelta(days=1)
        start = end.replace(day=1)
    elif period == 'year':
        start = today.replace(month=1, day=1)
        end = today
    else:
        return None, None
    return start, end


def _filter_by_period(qs, period, field='registered_at'):
    start, end = _period_bounds(period)
    if start and end:
        lookup = f'{field}__date__gte'
        return qs.filter(**{lookup: start, f'{field}__date__lte': end})
    return qs


def _daily_target(packages):
    """Target based on recent average daily registrations."""
    today = timezone.localdate()
    last_30 = today - timedelta(days=29)
    daily_counts = (
        packages.filter(registered_at__date__gte=last_30)
        .annotate(day=TruncDate('registered_at'))
        .values('day')
        .annotate(count=Count('id'))
        .values_list('count', flat=True)
    )
    counts = list(daily_counts)
    if counts:
        avg = sum(counts) / len(counts)
        return max(int(round(avg * 1.2)), 1)
    return 10


def build_dashboard_context(user, period='month'):
    packages = packages_for_user(user)
    today = timezone.localdate()
    period_packages = _filter_by_period(packages, period)

    total_packages = packages.count()
    in_transit = packages.filter(status=PackageStatus.IN_TRANSIT).count()
    arrived = packages.filter(
        status__in=[PackageStatus.ARRIVED, PackageStatus.READY_FOR_PICKUP]
    ).count()
    delivered = packages.filter(status=PackageStatus.DELIVERED).count()
    revenue_total = packages.aggregate(total=Sum('transport_fee'))['total'] or Decimal('0.00')
    revenue_period = period_packages.aggregate(total=Sum('transport_fee'))['total'] or Decimal('0.00')
    registered_period = period_packages.count()

    registered_today = packages.filter(registered_at__date=today).count()
    dispatched_today = packages.filter(
        status_history__status=PackageStatus.IN_TRANSIT,
        status_history__changed_at__date=today,
    ).distinct().count()
    delivered_today = packages.filter(delivered_at__date=today).count()
    daily_target = _daily_target(packages)

    def pct(value):
        return min(int((value / daily_target) * 100), 100) if daily_target else 0

    active_branches = Branch.objects.filter(is_active=True).count()
    if user.is_branch_officer and user.branch_id:
        active_branches = 1

    recent_shipments = packages.order_by('-registered_at')[:8]

    sent_counts = (
        period_packages.values('origin_branch__code', 'origin_branch__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:6]
    )
    branch_labels = [r['origin_branch__code'] or '?' for r in sent_counts]
    branch_sent_data = [r['count'] for r in sent_counts]

    received_counts = (
        _filter_by_period(packages, period)
        .values('destination_branch__code', 'destination_branch__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:6]
    )
    received_labels = [r['destination_branch__code'] or '?' for r in received_counts]
    received_data = [r['count'] for r in received_counts]

    if not branch_labels:
        branch_labels = ['No data']
        branch_sent_data = [0]
    if not received_labels:
        received_labels = ['No data']
        received_data = [0]

    status_map = dict(packages.values('status').annotate(count=Count('id')).values_list('status', 'count'))
    status_labels = [label for _, label, _ in STATUS_CHART_CONFIG]
    status_data = [status_map.get(key, 0) for key, _, _ in STATUS_CHART_CONFIG]
    status_colors = [color for _, _, color in STATUS_CHART_CONFIG]

    trend_start = today - timedelta(days=6)
    trend_rows = (
        packages.filter(registered_at__date__gte=trend_start)
        .annotate(day=TruncDate('registered_at'))
        .values('day')
        .annotate(
            packages=Count('id'),
            revenue=Sum('transport_fee'),
        )
        .order_by('day')
    )
    trend_by_day = {row['day']: row for row in trend_rows}

    trend_labels = []
    trend_packages = []
    trend_revenue = []
    for i in range(7):
        day = trend_start + timedelta(days=i)
        trend_labels.append(day.strftime('%b %d'))
        row = trend_by_day.get(day)
        trend_packages.append(row['packages'] if row else 0)
        trend_revenue.append(float(row['revenue'] or 0) if row else 0)

    branch_summary = []
    if user.is_admin_manager:
        for branch in Branch.objects.filter(is_active=True).order_by('name')[:5]:
            sent = packages.filter(origin_branch=branch).count()
            received = packages.filter(destination_branch=branch).count()
            branch_summary.append({
                'code': branch.code,
                'name': branch.name,
                'sent': sent,
                'received': received,
            })

    vehicles_active = Vehicle.objects.exclude(status=VehicleStatus.INACTIVE).count()
    vehicles_in_transit = Vehicle.objects.filter(status=VehicleStatus.IN_TRANSIT).count()

    subtitle = 'Overview of courier and cargo operations across all branches.'
    if user.is_branch_officer and user.branch:
        subtitle = f'Operations overview for {user.branch.name} ({user.branch.code}).'

    stats = {
        'total_packages': total_packages,
        'in_transit': in_transit,
        'arrived': arrived,
        'delivered': delivered,
        'revenue_total': f'{revenue_total:,.2f}',
        'revenue_period': f'{revenue_period:,.2f}',
        'registered_period': registered_period,
        'registered_today': registered_today,
        'dispatched_today': dispatched_today,
        'delivered_today': delivered_today,
        'daily_target': daily_target,
        'registered_pct': pct(registered_today),
        'dispatched_pct': pct(dispatched_today),
        'delivered_pct': pct(delivered_today),
        'active_branches': active_branches,
        'vehicles_active': vehicles_active,
        'vehicles_in_transit': vehicles_in_transit,
    }

    return {
        'active_nav': 'dashboard',
        'period': period,
        'period_label': PERIOD_CHOICES.get(period, 'This Month'),
        'period_choices': PERIOD_CHOICES,
        'page_subtitle': subtitle,
        'stats': stats,
        'recent_shipments': recent_shipments,
        'branch_summary': branch_summary,
        'branch_chart': {
            'labels': json.dumps(branch_labels),
            'sent': json.dumps(branch_sent_data),
            'received_labels': json.dumps(received_labels),
            'received': json.dumps(received_data),
        },
        'status_chart': {
            'labels': json.dumps(status_labels),
            'data': json.dumps(status_data),
            'colors': json.dumps(status_colors),
        },
        'trend_chart': {
            'labels': json.dumps(trend_labels),
            'packages': json.dumps(trend_packages),
            'revenue': json.dumps(trend_revenue),
        },
    }
