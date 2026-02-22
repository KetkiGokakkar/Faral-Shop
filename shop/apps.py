from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'

    def ready(self):
        # import signals so they are registered
        try:
            from backend import shop
        except Exception:
            pass