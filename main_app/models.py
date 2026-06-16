from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


def tenant_logo_path(instance, filename):
    ext = filename.rsplit('.', 1)[-1].lower()
    return f'tenant_logos/{instance.schema_name}/logo.{ext}'


class Client(TenantMixin):
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100, blank=True, help_text='Shown in the app header and login page.')
    tagline = models.CharField(max_length=150, blank=True, default='Courier & Cargo Management')
    logo = models.ImageField(upload_to=tenant_logo_path, blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#3b82f6', help_text='Main brand color (hex).')
    sidebar_color = models.CharField(max_length=7, default='#1e2a4a', help_text='Sidebar background color (hex).')
    paid_until = models.DateField(null=True, blank=True)
    on_trial = models.BooleanField(null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)

    auto_create_schema = True

    def __str__(self):
        return self.display_name or self.name


class Domain(DomainMixin):
    pass