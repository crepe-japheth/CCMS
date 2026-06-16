# Generated manually for tenant branding fields

import main_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='display_name',
            field=models.CharField(blank=True, help_text='Shown in the app header and login page.', max_length=100),
        ),
        migrations.AddField(
            model_name='client',
            name='tagline',
            field=models.CharField(blank=True, default='Courier & Cargo Management', max_length=150),
        ),
        migrations.AddField(
            model_name='client',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to=main_app.models.tenant_logo_path),
        ),
        migrations.AddField(
            model_name='client',
            name='primary_color',
            field=models.CharField(default='#3b82f6', help_text='Main brand color (hex).', max_length=7),
        ),
        migrations.AddField(
            model_name='client',
            name='sidebar_color',
            field=models.CharField(default='#1e2a4a', help_text='Sidebar background color (hex).', max_length=7),
        ),
    ]
