from django.contrib import admin
from django_tenants.admin import TenantAdminMixin

from main_app.models import Client


@admin.register(Client)
class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'display_name', 'schema_name', 'paid_until')
    fieldsets = (
        (None, {'fields': ('name', 'schema_name', 'paid_until', 'on_trial')}),
        ('Branding', {'fields': ('display_name', 'tagline', 'logo', 'primary_color', 'sidebar_color')}),
    )
