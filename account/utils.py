def get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_audit(user, action, description='', request=None):
    from .models import AuditLog

    ip_address = get_client_ip(request) if request else None
    AuditLog.objects.create(
        user=user,
        action=action,
        description=description,
        ip_address=ip_address,
    )
