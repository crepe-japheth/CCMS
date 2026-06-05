import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.shortcuts import render
from django.utils import timezone

from ccms_app.models import Branch, Package, PackageStatus
from ccms_app.services import packages_for_user


@login_required
def dashboard(request):
    packages = packages_for_user(request.user)
    today = timezone.localdate()

    total_packages = packages.count()
    in_transit = packages.filter(status=PackageStatus.IN_TRANSIT).count()
    delivered = packages.filter(status=PackageStatus.DELIVERED).count()
    revenue = packages.aggregate(total=Sum('transport_fee'))['total'] or Decimal('0.00')

    registered_today = packages.filter(registered_at__date=today).count()
    dispatched_today = packages.filter(
        status_history__status=PackageStatus.IN_TRANSIT,
        status_history__changed_at__date=today,
    ).distinct().count()
    delivered_today = packages.filter(delivered_at__date=today).count()
    daily_target = 65

    def pct(value):
        return min(int((value / daily_target) * 100), 100) if daily_target else 0

    active_branches = Branch.objects.filter(is_active=True).count()

    recent_shipments = [
        {
            'tracking_number': p.tracking_number,
            'origin': p.origin_branch.code,
            'destination': p.destination_branch.code,
            'status': p.status_label,
            'status_class': p.status_css_class,
            'fee': p.transport_fee,
        }
        for p in packages.order_by('-registered_at')[:8]
    ]

    branch_counts = (
        packages.values('origin_branch__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )
    branch_labels = [b['origin_branch__name'] or 'Unknown' for b in branch_counts]
    branch_data = [b['count'] for b in branch_counts]

    if not branch_labels:
        branch_labels = ['No data yet']
        branch_data = [0]

    status_counts = packages.values('status').annotate(count=Count('id'))
    status_map = {s['status']: s['count'] for s in status_counts}
    status_labels = ['Registered', 'In Transit', 'Arrived', 'Delivered', 'Cancelled']
    status_keys = [
        PackageStatus.REGISTERED,
        PackageStatus.IN_TRANSIT,
        PackageStatus.ARRIVED,
        PackageStatus.DELIVERED,
        PackageStatus.CANCELLED,
    ]
    status_data = [status_map.get(key, 0) for key in status_keys]

    stats = {
        'total_packages': total_packages,
        'in_transit': in_transit,
        'delivered': delivered,
        'revenue': f'{revenue:,.2f}',
        'registered_today': registered_today,
        'dispatched_today': dispatched_today,
        'delivered_today': delivered_today,
        'daily_target': daily_target,
        'registered_pct': pct(registered_today),
        'dispatched_pct': pct(dispatched_today),
        'delivered_pct': pct(delivered_today),
        'active_branches': active_branches,
    }

    context = {
        'active_nav': 'dashboard',
        'stats': stats,
        'recent_shipments': recent_shipments,
        'branch_chart': {
            'labels': json.dumps(branch_labels),
            'data': json.dumps(branch_data),
        },
        'status_chart': {
            'labels': json.dumps(status_labels),
            'data': json.dumps(status_data),
        },
    }
    return render(request, 'ccms_app/dashboard.html', context)
