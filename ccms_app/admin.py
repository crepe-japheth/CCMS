from django.contrib import admin

from .models import Branch, Package, PackageStatusHistory, Vehicle


class PackageStatusHistoryInline(admin.TabularInline):
    model = PackageStatusHistory
    extra = 0
    readonly_fields = ('status', 'changed_by', 'changed_at', 'notes')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'location', 'contact_number', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'location')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'vehicle_type', 'driver_name', 'driver_phone', 'status')
    list_filter = ('status', 'vehicle_type')
    search_fields = ('plate_number', 'driver_name', 'driver_phone')


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = (
        'tracking_number',
        'sender_full_name',
        'receiver_full_name',
        'origin_branch',
        'destination_branch',
        'status',
        'transport_fee',
        'registered_at',
    )
    list_filter = ('status', 'package_type', 'origin_branch', 'destination_branch')
    search_fields = (
        'tracking_number',
        'sender_full_name',
        'receiver_full_name',
        'sender_phone',
        'receiver_phone',
    )
    readonly_fields = ('tracking_number', 'registered_at', 'created_at', 'updated_at')
    autocomplete_fields = ('origin_branch', 'destination_branch', 'assigned_vehicle', 'registered_by')
    inlines = [PackageStatusHistoryInline]

    fieldsets = (
        ('Tracking', {'fields': ('tracking_number', 'status')}),
        ('Sender', {'fields': ('sender_full_name', 'sender_id_number', 'sender_phone')}),
        ('Receiver', {'fields': ('receiver_full_name', 'receiver_id_number', 'receiver_phone')}),
        ('Shipment', {
            'fields': (
                'package_type', 'description', 'quantity', 'weight',
                'origin_branch', 'destination_branch', 'assigned_vehicle', 'transport_fee',
            ),
        }),
        ('Registration', {'fields': ('registered_by', 'registered_at')}),
        ('Arrival', {'fields': ('received_by', 'received_at_branch', 'arrived_at')}),
        ('Delivery', {'fields': ('delivered_by', 'delivered_at', 'delivery_receiver_id_number')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(PackageStatusHistory)
class PackageStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('package', 'status', 'changed_by', 'changed_at')
    list_filter = ('status', 'changed_at')
    search_fields = ('package__tracking_number', 'notes')
    readonly_fields = ('package', 'status', 'changed_by', 'changed_at', 'notes')
