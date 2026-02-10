"""Команда которым заполняем базу данных ингредиентами."""


from .base_load import LoadJsonCommand
from recipes.models import Ingredients


class Command(LoadJsonCommand):
    """Класс загружает ингредиенты из файла json/ingredients."""

    help = 'Загружает ингредиенты из файла json/ingredients.'
    model = Ingredients
    path = '/app/data/ingredients.json'
