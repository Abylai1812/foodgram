"""Базовый класс которым заполняем базу данных ингредиентами и тегами."""


import json

from django.core.management.base import BaseCommand


class LoadJsonCommand(BaseCommand):
    """Общий базовый класс для загрузки ингредиентов и тегов."""

    model = None
    path = None

    def handle(self, *args, **options):
        """Метод загрузки ингредиенты из файла json/ingredients."""
        try:
            with open(self.path, 'r', encoding='utf-8') as file:
                data_list = [
                    self.model(**item) for item in json.load(file)
                ]
            new_entries = self.model.objects.bulk_create(
                data_list,
                ignore_conflicts=True
            )

            self.stdout.write(self.style.SUCCESS(
                f'Фикстура: {self.path} загружены!'
                f'{len(new_entries)} {self.model.__name__} успешно добавлены')
            )

        except Exception as error:
            self.stdout.write(
                self.style.ERROR(
                    f'Фикстура {self.path}: Ошибка загрузки данных: {error}'
                )
            )
