from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class CustomsRegistryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customs_registry'
    verbose_name = _('customs_registries')

    def ready(self):
        import customs_registry.signals   # Import the signals file
