# myapp/apps.py
from django.apps import AppConfig

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        # import signals to ensure they are registered
        try:
            import myapp.signals  # noqa: F401
        except Exception:
            # during migrations imports may fail; don't crash
            pass
