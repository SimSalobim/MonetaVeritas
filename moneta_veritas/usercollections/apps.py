# usercollections/apps.py
from django.apps import AppConfig


class UsercollectionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usercollections'
    verbose_name = 'Коллекции пользователей'