"""Тесты создания рецепта в проекте Foodgram."""

import base64
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from foodgram_api.models import Recipes, Ingredients, Tags

User = get_user_model()


class RecipeCreateAPITestCase(TestCase):
    """Тест создание рецепта."""

    def setUp(self):
        """Подготовка данных для тестов."""
        self.guest_client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.user)

        self.tag = Tags.objects.create(
            name='Завтрак',
            slug='breakfast'
        )

        self.ingredient = Ingredients.objects.create(
            name='Яйцо',
            measurement_unit='шт'
        )

    def get_valid_recipe_data(self):
        """
        Возвращает валидный набор обязательных полей.

        Для создания рецепта.
        """
        image_bytes = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01'
            b'\x00H\x00H\x00\x00\xff\xd9'
        )
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        return {
            'name': 'Test recipe',
            'text': 'Test text',
            'cooking_time': 10,
            'tags': [self.tag.id],
            'ingredients': [
                {
                    'id': self.ingredient.id,
                    'amount': 2
                }
            ],
            'image': f'data:image/jpeg;base64,{image_base64}'
        }

    def test_guest_cannot_create_recipe(self):
        """Гость не может создать рецепт."""
        response = self.guest_client.post(
            '/api/recipes/',
            data=self.get_valid_recipe_data(),
            format='json'
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_authorized_user_can_create_recipe(self):
        """
        Авторизованный пользователь может создать рецепт.

        Обязательными полями.
        """
        response = self.auth_client.post(
            '/api/recipes/',
            data=self.get_valid_recipe_data(),
            format='json'
        )

        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(
            Recipes.objects.filter(
                name='Test recipe',
                author=self.user
            ).exists()
        )
