from django.apps import AppConfig


class MemesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'memes'

    def ready(self):
        # Импортируем сигналы только после полной загрузки приложения
        try:
            import memes.signals
        except ImportError:
            pass