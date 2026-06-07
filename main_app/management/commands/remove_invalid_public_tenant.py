from django.core.management.base import BaseCommand, CommandError

from main_app.models import Client, Domain


class Command(BaseCommand):
    help = 'Remove invalid Client tenant that incorrectly uses schema_name "public".'

    def add_arguments(self, parser):
        parser.add_argument('--noinput', action='store_true', help='Skip confirmation')

    def handle(self, *args, **options):
        try:
            client = Client.objects.get(schema_name='public')
        except Client.DoesNotExist:
            self.stdout.write(self.style.SUCCESS('No invalid public tenant found.'))
            return

        if not options['noinput']:
            confirm = input(
                'Delete tenant record "public" and its domains? '
                '(Does NOT drop the PostgreSQL public schema.) [y/N]: '
            )
            if confirm.lower() != 'y':
                self.stdout.write('Aborted.')
                return

        domains = list(Domain.objects.filter(tenant=client).values_list('domain', flat=True))
        Domain.objects.filter(tenant=client).delete()
        client.delete()

        self.stdout.write(self.style.SUCCESS(
            f'Removed invalid tenant "public" and domains: {", ".join(domains) or "(none)"}'
        ))
        self.stdout.write(
            'Now run: python manage.py setup_saas_tenant --name ccms --schema ccms --domain localhost --create-superuser'
        )
