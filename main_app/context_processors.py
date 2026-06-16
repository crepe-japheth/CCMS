from django.db import connection

from .branding import get_tenant_branding


def tenant_branding(request):
    tenant = getattr(connection, 'tenant', None)
    schema_name = getattr(tenant, 'schema_name', None)
    if schema_name == 'public':
        tenant = None
    return {'tenant_branding': get_tenant_branding(tenant)}
