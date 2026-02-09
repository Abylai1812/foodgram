"""ViewSet'ы для recipes для проекта Foodgram.

Модуль содержит ViewSet'ы для обработки CRUD операций.
"""


from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from recipes.models import Recipes


def redirect_to_recipe(request, pk):
    """Перенаправляет с короткой ссылки на страницу рецепта."""
    if not Recipes.objects.filter(pk=pk).exists():
       return HttpResponseNotFound('Рецепт не найден')
    return redirect(f'/recipes/{pk}/')
