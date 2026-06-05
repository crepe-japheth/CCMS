from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Package, PackageStatusHistory


@receiver(post_save, sender=Package)
def create_initial_status_history(sender, instance, created, **kwargs):
    if created and not instance.status_history.exists():
        PackageStatusHistory.objects.create(
            package=instance,
            status=instance.status,
            changed_by=instance.registered_by,
            notes='Package registered.',
        )
