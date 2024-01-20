from django.apps import AppConfig


class PhotorollConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'photoroll'

    def ready(self):
        import photoroll.signals