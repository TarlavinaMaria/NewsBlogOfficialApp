from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'
    verbose_name = 'Новость' # имя модели в единственном числе
    verbose_name_plural = 'Новости' # имя модели во множественном числе

    def ready(self):
        import news.signals