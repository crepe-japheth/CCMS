from decimal import Decimal

from django.core.management.base import BaseCommand

from account.models import User, UserRole
from ccms_app.models import Branch, Package, PackageStatus, PackageType, Vehicle, VehicleStatus
from ccms_app.services import create_package_with_status, record_status_change


class Command(BaseCommand):
    help = 'Create demo branches, users, vehicles, and packages for development.'

    def handle(self, *args, **options):
        branches_data = [
            {
                'name': 'Nairobi Central',
                'code': 'NBO-01',
                'location': 'Nairobi, Kenya',
                'contact_number': '+254700000001',
            },
            {
                'name': 'Mombasa Port',
                'code': 'MBA-01',
                'location': 'Mombasa, Kenya',
                'contact_number': '+254700000002',
            },
            {
                'name': 'Kisumu Hub',
                'code': 'KSM-01',
                'location': 'Kisumu, Kenya',
                'contact_number': '+254700000003',
            },
        ]

        branches = []
        for data in branches_data:
            branch, created = Branch.objects.get_or_create(code=data['code'], defaults=data)
            branches.append(branch)
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  [{status}] Branch: {branch.name}')

        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'full_name': 'System Administrator',
                'email': 'admin@ccms.local',
                'phone_number': '+254700000100',
                'role': UserRole.ADMIN_MANAGER,
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('  [Created] Admin user: admin / admin123'))
        else:
            self.stdout.write('  [Exists] Admin user: admin')

        officer_user, created = User.objects.get_or_create(
            username='officer',
            defaults={
                'full_name': 'Branch Officer',
                'email': 'officer@ccms.local',
                'phone_number': '+254700000200',
                'role': UserRole.BRANCH_OFFICER,
                'branch': branches[0],
            },
        )
        if created:
            officer_user.set_password('officer123')
            officer_user.save()
            self.stdout.write(self.style.SUCCESS('  [Created] Branch Officer: officer / officer123'))
        else:
            self.stdout.write('  [Exists] Branch Officer: officer')

        vehicles_data = [
            {
                'plate_number': 'KCA 123A',
                'vehicle_type': 'Van',
                'driver_name': 'James Otieno',
                'driver_phone': '+254711000001',
                'status': VehicleStatus.AVAILABLE,
            },
            {
                'plate_number': 'KCB 456B',
                'vehicle_type': 'Truck',
                'driver_name': 'Mary Wanjiku',
                'driver_phone': '+254711000002',
                'status': VehicleStatus.IN_TRANSIT,
            },
        ]

        vehicles = []
        for data in vehicles_data:
            vehicle, created = Vehicle.objects.get_or_create(
                plate_number=data['plate_number'],
                defaults=data,
            )
            vehicles.append(vehicle)
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  [{status}] Vehicle: {vehicle.plate_number}')

        if Package.objects.exists():
            self.stdout.write('  [Skip] Sample packages already exist')
        else:
            samples = [
                {
                    'sender_full_name': 'John Kamau',
                    'sender_id_number': 'ID12345678',
                    'sender_phone': '+254722000001',
                    'receiver_full_name': 'Jane Akinyi',
                    'receiver_id_number': 'ID87654321',
                    'receiver_phone': '+254722000002',
                    'package_type': PackageType.PARCEL,
                    'description': 'Electronics — laptop and accessories',
                    'quantity': 1,
                    'weight': Decimal('3.50'),
                    'origin_branch': branches[0],
                    'destination_branch': branches[1],
                    'assigned_vehicle': vehicles[1],
                    'transport_fee': Decimal('2500.00'),
                    'status': PackageStatus.IN_TRANSIT,
                },
                {
                    'sender_full_name': 'Peter Ochieng',
                    'sender_id_number': 'ID11223344',
                    'sender_phone': '+254722000003',
                    'receiver_full_name': 'Grace Muthoni',
                    'receiver_id_number': 'ID44332211',
                    'receiver_phone': '+254722000004',
                    'package_type': PackageType.DOCUMENTS,
                    'description': 'Legal documents',
                    'quantity': 1,
                    'weight': Decimal('0.50'),
                    'origin_branch': branches[0],
                    'destination_branch': branches[2],
                    'assigned_vehicle': vehicles[0],
                    'transport_fee': Decimal('800.00'),
                    'status': PackageStatus.REGISTERED,
                },
                {
                    'sender_full_name': 'David Mutua',
                    'sender_id_number': 'ID55667788',
                    'sender_phone': '+254722000005',
                    'receiver_full_name': 'Lucy Chebet',
                    'receiver_id_number': 'ID88776655',
                    'receiver_phone': '+254722000006',
                    'package_type': PackageType.CARGO,
                    'description': 'Household goods',
                    'quantity': 3,
                    'weight': Decimal('45.00'),
                    'origin_branch': branches[1],
                    'destination_branch': branches[0],
                    'assigned_vehicle': vehicles[1],
                    'transport_fee': Decimal('8500.00'),
                    'status': PackageStatus.DELIVERED,
                },
            ]

            for data in samples:
                target_status = data.pop('status')
                package = Package(
                    registered_by=officer_user,
                    **data,
                )
                create_package_with_status(package, user=officer_user)
                if target_status != PackageStatus.REGISTERED:
                    record_status_change(
                        package,
                        target_status,
                        user=officer_user,
                        notes='Demo status update.',
                    )
                self.stdout.write(self.style.SUCCESS(f'  [Created] Package: {package.tracking_number}'))

        self.stdout.write(self.style.SUCCESS('\nDemo data ready. Sign in at /account/login/'))
