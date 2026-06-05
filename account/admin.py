from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AuditLog, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'full_name', 'email', 'role', 'branch', 'status', 'is_staff')
    list_filter = ('role', 'status', 'branch', 'is_staff')
    search_fields = ('username', 'full_name', 'email', 'phone_number')
    ordering = ('full_name',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('CCMS Profile', {
            'fields': ('full_name', 'phone_number', 'role', 'status', 'branch'),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('CCMS Profile', {
            'fields': ('full_name', 'phone_number', 'role', 'status', 'branch'),
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'user__full_name', 'description')
    readonly_fields = ('user', 'action', 'description', 'ip_address', 'timestamp')
