from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'
    verbose_name = 'Noticias'

    def ready(self):
        """
        Import signals when the app is ready

        This ensures signal handlers are registered at Django startup.
        """
        import news.signals  # noqa: F401