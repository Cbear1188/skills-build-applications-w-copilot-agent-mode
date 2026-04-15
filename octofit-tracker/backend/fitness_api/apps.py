from django.apps import AppConfig


class FitnessApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fitness_api'

    def ready(self):
        from . import signals  # noqa: F401
