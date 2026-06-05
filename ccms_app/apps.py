from django.apps import AppConfig


class CcmsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ccms_app'

    def ready(self):
        import ccms_app.signals  # noqa: F401
