"""Команда которым заполняем базу данных тегами."""


from recipes.models import Tags

from commands.base_load import LoadJsonCommand


class Command(LoadJsonCommand):
    """Класс загружает тегов из файла json/tags."""

    help = 'Загружает тегов из файла json/tags.'
    model = Tags
    path = '/app/data/tags.json'
