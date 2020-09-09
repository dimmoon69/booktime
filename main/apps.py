from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'main'
    verbose_name = 'Меню магазина'

    def ready(self):
        from . import signals