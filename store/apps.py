from django.apps import AppConfig


class StoreConfig(AppConfig):
    name = 'store'

    def ready(self):
        try:
            import store.signals  # noqa: F401
        except ImportError:
            pass