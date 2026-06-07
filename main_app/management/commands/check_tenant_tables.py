from django.core.management.base import BaseCommand
from django.db import connection
from django_tenants.utils import schema_context

from main_app.models import Client


class Command(BaseCommand):
    help = 'Check tenant tables exist in each schema.'

    def handle(self, *args, **options):
        for client in Client.objects.all():
            with schema_context(client.schema_name):
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT tablename FROM pg_tables
                        WHERE schemaname = %s
                        AND tablename IN ('django_session', 'account_user', 'main_app_client')
                        """,
                        [client.schema_name],
                    )
                    tables = [row[0] for row in cursor.fetchall()]
            self.stdout.write(f'{client.schema_name}: {tables or "(none)"}')
