from django.contrib import messages
from django.shortcuts import redirect, render

from account.decorators import admin_required

from .report_exports import export_excel, export_pdf
from .report_services import REPORT_DEFINITIONS, generate_report, get_reports_by_category


def _parse_date_param(value):
    if not value:
        return None
    try:
        from datetime import datetime
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


@admin_required
def reports_hub(request):
    category_labels = {
        'operational': 'Operational Reports',
        'financial': 'Financial Reports',
        'activity': 'User Activity Reports',
    }
    sections = [
        {'key': key, 'label': category_labels[key], 'reports': reports}
        for key, reports in get_reports_by_category().items()
        if reports
    ]
    return render(request, 'ccms_app/reports/hub.html', {
        'active_nav': 'reports',
        'sections': sections,
    })


@admin_required
def report_view(request, slug):
    if slug not in REPORT_DEFINITIONS:
        messages.error(request, 'Report not found.')
        return redirect('ccms_app:reports_hub')

    date_from = _parse_date_param(request.GET.get('date_from'))
    date_to = _parse_date_param(request.GET.get('date_to'))

    report_data = generate_report(slug, date_from=date_from, date_to=date_to)

    return render(request, 'ccms_app/reports/view.html', {
        'active_nav': 'reports',
        'report': report_data,
        'date_from': report_data['date_from'].isoformat(),
        'date_to': report_data['date_to'].isoformat(),
    })


@admin_required
def report_export(request, slug, fmt):
    if slug not in REPORT_DEFINITIONS:
        messages.error(request, 'Report not found.')
        return redirect('ccms_app:reports_hub')

    if fmt not in ('pdf', 'excel'):
        messages.error(request, 'Invalid export format.')
        return redirect('ccms_app:report_view', slug=slug)

    date_from = _parse_date_param(request.GET.get('date_from'))
    date_to = _parse_date_param(request.GET.get('date_to'))
    report_data = generate_report(slug, date_from=date_from, date_to=date_to)

    if fmt == 'pdf':
        return export_pdf(report_data)
    return export_excel(report_data)
