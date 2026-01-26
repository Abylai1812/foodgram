"""Тесты создания рецепта в проекте Foodgram."""

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

from recipes.models import Recipe, Ingredient, Tag

User = get_user_model()


class RecipeCreateAPITestCase(TestCase):
    """Тест создание рецепта."""

    def setUp(self):
        """Подготовка данных для тестов."""
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

        self.tag = Tag.objects.create(
            name='Завтрак',
            slug='breakfast'
        )

        self.ingredient = Ingredient.objects.create(
            name='Яйцо',
            measurement_unit='шт'
        )

    def get_valid_recipe_data(self):
        """
        Возвращает валидный набор обязательных полей.

        Для создания рецепта.
        """
        image = SimpleUploadedFile(
            name='test.jpg',
            content=b'test_image',
            content_type='image/jpeg'
        )

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
            'image': image
        }

    def test_guest_cannot_create_recipe(self):
        """Гость не может создать рецепт."""
        response = self.guest_client.post(
            '/api/recipes/',
            data=self.get_valid_recipe_data()
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_authorized_user_can_create_recipe(self):
        """
        Авторизованный пользователь может создать рецепт.

        Обязательными полями.
        """
        response = self.auth_client.post(
            '/api/recipes/',
            data=self.get_valid_recipe_data()
        )

        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(
            Recipe.objects.filter(
                name='Test recipe',
                author=self.user
            ).exists()
        )
