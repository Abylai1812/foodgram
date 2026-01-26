"""
Проверка получение список рецептов и прав доступа. 
"""

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from recipes.models import Recipe

User = get_user_model()


class FoodgramAPITestCase(TestCase):
    """
    Набор тестов для эндпоинта.
    """
    def setUp(self):
        """Подготовка тестовых данных."""
        self.guest_client = Client()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.auth_client = Client()
        self.auth_client.login(
            username='testuser',
            password='testpassword'
        )

    def test_recipe_list_exists(self):
        """Проверка доступности списка рецептов для гостя."""
        response = self.guest_client.get('/api/recipes/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_recipe_creation_forbidden_for_guest(self):
        """Гость не может создать рецепт."""
        data = {
            'name': 'Test recipe',
            'text': 'Test text',
            'cooking_time': 10
        }
        response = self.guest_client.post('/api/recipes/', data=data)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_recipe_creation_for_authorized_user(self):
        """Авторизованный пользователь может создать рецепт."""
        data = {
            'name': 'Test recipe',
            'text': 'Test text',
            'cooking_time': 10
        }
        response = self.auth_client.post('/api/recipes/', data=data)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(
            Recipe.objects.filter(name='Test recipe').exists()
        )
