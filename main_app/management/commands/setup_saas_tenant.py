from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from main_app.models import Client, Domain


class Command(BaseCommand):
    help = (
        'Create a tenant with domain, run tenant migrations, and optionally create a superuser. '
        'Do NOT use schema_name "public" — that name is reserved for shared tables.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--name', required=True, help='Tenant display name')
        parser.add_argument('--schema', required=True, help='PostgreSQL schema name (e.g. ccms, acme)')
        parser.add_argument('--domain', required=True, help='Domain hostname (e.g. localhost or acme.localhost)')
        parser.add_argument('--create-superuser', action='store_true', help='Run create_tenant_superuser after migrate')

    def handle(self, *args, **options):
        schema = options['schema'].strip().lower()
        domain_name = options['domain'].strip().lower()

        if schema == 'public':
            raise CommandError(
                'Schema name "public" is reserved for django-tenants shared tables. '
                'Choose another name, e.g. "ccms" or "demo".'
            )

        client, created = Client.objects.get_or_create(
            schema_name=schema,
            defaults={
                'name': options['name'],
                'on_trial': True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created tenant: {schema}'))
        else:
            self.stdout.write(f'Tenant already exists: {schema}')

        domain, d_created = Domain.objects.get_or_create(
            domain=domain_name,
            defaults={'tenant': client, 'is_primary': True},
        )
        if not d_created and domain.tenant_id != client.id:
            domain.tenant = client
            domain.is_primary = True
            domain.save(update_fields=['tenant', 'is_primary'])
            self.stdout.write(self.style.WARNING(f'Reassigned domain {domain_name} to tenant {schema}'))
        elif d_created:
            self.stdout.write(self.style.SUCCESS(f'Created domain: {domain_name}'))

        self.stdout.write('Running tenant migrations...')
        call_command('migrate_schemas', '--tenant', schema_name=schema, verbosity=1)

        if options['create_superuser']:
            self.stdout.write('Create superuser for this tenant:')
            call_command('create_tenant_superuser', schema_name=schema)

        self.stdout.write(self.style.SUCCESS(
            f'\nTenant ready. Open http://{domain_name}:8000/ (add to hosts file if using subdomains).'
        ))
        self.stdout.write('Create users with: python manage.py create_tenant_superuser -s ' + schema)
