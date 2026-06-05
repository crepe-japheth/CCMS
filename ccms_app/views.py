from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .dashboard_services import PERIOD_CHOICES, build_dashboard_context


@login_required
def dashboard(request):
    period = request.GET.get('period', 'month')
    if period not in PERIOD_CHOICES:
        period = 'month'

    context = build_dashboard_context(request.user, period=period)
    return render(request, 'ccms_app/dashboard.html', context)
