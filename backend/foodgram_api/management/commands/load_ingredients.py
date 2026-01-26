"""Команда которым заполняем базу данных ингредиентами."""

import json
import os
from django.core.management.base import BaseCommand
from foodgram_api.models import Ingredients


class Command(BaseCommand):
    """Класс загружает ингредиенты из файла json/ingredients."""

    help = 'Загружает ингредиенты из файла json/ingredients.'

    def handle(self, *args, **options):
        """Метод загрузки ингредиенты из файла json/ingredients."""
        path = '/app/data/ingredients.json'

        if not os.path.exists(path):
            self.stdout.write(
                self.style.ERROR(f'Файл не найден по пути {path}')
            )
            return

        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)

            for item in data:
                Ingredients.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
        self.stdout.write(self.style.SUCCESS('Ингредиенты успешно загружены!'))
