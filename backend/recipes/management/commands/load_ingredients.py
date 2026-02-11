"""Команда которым заполняем базу данных ингредиентами."""


from recipes.models import Ingredients

from commands.base_load import LoadJsonCommand


class Command(LoadJsonCommand):
    """Класс загружает ингредиенты из файла json/ingredients."""

    help = 'Загружает ингредиенты из файла json/ingredients.'
    model = Ingredients
    path = '/app/data/ingredients.json'
