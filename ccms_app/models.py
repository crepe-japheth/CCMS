from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


class Branch(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'branches'

    def __str__(self):
        return f'{self.name} ({self.code})'


class VehicleStatus(models.TextChoices):
    AVAILABLE = 'available', 'Available'
    IN_TRANSIT = 'in_transit', 'In Transit'
    MAINTENANCE = 'maintenance', 'Under Maintenance'
    INACTIVE = 'inactive', 'Inactive'


class Vehicle(models.Model):
    plate_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=100)
    driver_name = models.CharField(max_length=255)
    driver_phone = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20,
        choices=VehicleStatus.choices,
        default=VehicleStatus.AVAILABLE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['plate_number']

    def __str__(self):
        return f'{self.plate_number} — {self.driver_name}'


class PackageType(models.TextChoices):
    DOCUMENTS = 'documents', 'Documents'
    PARCEL = 'parcel', 'Parcel'
    CARGO = 'cargo', 'Cargo'
    OTHER = 'other', 'Other'


class PackageStatus(models.TextChoices):
    REGISTERED = 'registered', 'Registered'
    READY_FOR_DISPATCH = 'ready_for_dispatch', 'Ready for Dispatch'
    IN_TRANSIT = 'in_transit', 'In Transit'
    ARRIVED = 'arrived', 'Arrived at Destination'
    READY_FOR_PICKUP = 'ready_for_pickup', 'Ready for Pickup'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'


class Package(models.Model):
    tracking_number = models.CharField(max_length=30, unique=True, editable=False)

    sender_full_name = models.CharField(max_length=255)
    sender_id_number = models.CharField(max_length=50)
    sender_phone = models.CharField(max_length=20)

    receiver_full_name = models.CharField(max_length=255)
    receiver_id_number = models.CharField(max_length=50)
    receiver_phone = models.CharField(max_length=20)

    package_type = models.CharField(max_length=20, choices=PackageType.choices)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1)
    weight = models.DecimalField(max_digits=10, decimal_places=2)

    origin_branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name='outgoing_packages',
    )
    destination_branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name='incoming_packages',
    )
    assigned_vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shipments',
    )

    transport_fee = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=30,
        choices=PackageStatus.choices,
        default=PackageStatus.REGISTERED,
    )

    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='registered_packages',
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_packages',
    )
    received_at_branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_packages',
    )
    arrived_at = models.DateTimeField(null=True, blank=True)

    delivered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delivered_packages',
    )
    delivered_at = models.DateTimeField(null=True, blank=True)
    delivery_receiver_id_number = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-registered_at']

    def __str__(self):
        return self.tracking_number

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            from .services import generate_tracking_number
            self.tracking_number = generate_tracking_number()
        super().save(*args, **kwargs)

    @property
    def status_label(self):
        return self.get_status_display()

    @property
    def status_css_class(self):
        mapping = {
            PackageStatus.REGISTERED: 'registered',
            PackageStatus.READY_FOR_DISPATCH: 'ready',
            PackageStatus.IN_TRANSIT: 'in-transit',
            PackageStatus.ARRIVED: 'arrived',
            PackageStatus.READY_FOR_PICKUP: 'ready',
            PackageStatus.DELIVERED: 'delivered',
            PackageStatus.CANCELLED: 'cancelled',
        }
        return mapping.get(self.status, 'registered')


class PackageStatusHistory(models.Model):
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name='status_history',
    )
    status = models.CharField(max_length=30, choices=PackageStatus.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='package_status_changes',
    )
    changed_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'package status histories'

    def __str__(self):
        return f'{self.package.tracking_number} → {self.get_status_display()}'
