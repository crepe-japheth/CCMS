from django.contrib import messages
from django.db import connection
from django.shortcuts import redirect, render
from django_tenants.utils import schema_context

from account.decorators import admin_required

from .forms import TenantBrandingForm


@admin_required
def branding_settings(request):
    tenant = connection.tenant
    if not tenant or tenant.schema_name == 'public':
        messages.error(request, 'Branding is only available inside a tenant.')
        return redirect('ccms_app:dashboard')

    form = TenantBrandingForm(request.POST or None, request.FILES or None, instance=tenant)
    if request.method == 'POST' and form.is_valid():
        with schema_context('public'):
            form.save()
        messages.success(request, 'Tenant branding updated successfully.')
        return redirect('main_app:branding_settings')

    return render(request, 'main_app/branding_settings.html', {
        'active_nav': 'branding',
        'form': form,
        'tenant': tenant,
    })
