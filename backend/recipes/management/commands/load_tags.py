"""Команда которым заполняем базу данных тегами."""


from .base_load import LoadJsonCommand
from recipes.models import Tags


class Command(LoadJsonCommand):
    """Класс загружает тегов из файла json/tags."""

    help = 'Загружает тегов из файла json/tags.'
    model = Tags
    path = '/app/data/tags.json'
