from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    ADMIN_MANAGER = 'admin_manager', 'System Administrator / Manager'
    BRANCH_OFFICER = 'branch_officer', 'Branch Officer'


class UserStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'


class User(AbstractUser):
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.BRANCH_OFFICER,
    )
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE,
    )
    branch = models.ForeignKey(
        'ccms_app.Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff',
    )

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return self.full_name or self.username

    @property
    def is_admin_manager(self):
        return self.role == UserRole.ADMIN_MANAGER

    @property
    def is_branch_officer(self):
        return self.role == UserRole.BRANCH_OFFICER

    @property
    def is_account_active(self):
        return self.status == UserStatus.ACTIVE

    @property
    def role_label(self):
        return self.get_role_display()

    def get_initials(self):
        parts = self.full_name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        if parts:
            return parts[0][0].upper()
        return self.username[:1].upper()


class AuditLog(models.Model):
    class Action(models.TextChoices):
        LOGIN = 'login', 'Login'
        LOGOUT = 'logout', 'Logout'
        USER_CREATED = 'user_created', 'User Created'
        USER_UPDATED = 'user_updated', 'User Updated'
        BRANCH_CREATED = 'branch_created', 'Branch Created'
        BRANCH_UPDATED = 'branch_updated', 'Branch Updated'
        PACKAGE_REGISTERED = 'package_registered', 'Package Registered'
        PACKAGE_STATUS_CHANGED = 'package_status_changed', 'Package Status Changed'
        PACKAGE_ARRIVAL = 'package_arrival', 'Package Arrival Confirmed'
        PACKAGE_DELIVERED = 'package_delivered', 'Package Delivered'
        VEHICLE_ASSIGNED = 'vehicle_assigned', 'Vehicle Assigned'

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=50, choices=Action.choices)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        username = self.user.username if self.user else 'Unknown'
        return f'{username} — {self.get_action_display()}'
