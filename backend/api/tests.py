from http import HTTPStatus

from django.test import TestCase
from rest_framework.test import APIClient

from recipes.models import Ingredient, Tag
from users.models import User


class RecipesAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='auth_user',
            password='testpassword'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.tag = Tag.objects.create(
            name='Test Tag',
            color='#FFFFFF',
            slug='test-tag'
        )
        self.ingredient = Ingredient.objects.create(
            name='Test Ingredient',
            measurement_unit='g'
        )

    def test_list_exists(self):
        """Проверка доступности списка рецептов."""
        response = self.client.get('/api/recipes/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_download_shopping_cart(self):
        """Проверка недоступности скачивания списка покупок."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/recipes/download_shopping_cart/')
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_create_recipe(self):
        """Проверка возможности создания рецепта."""
        data = {
            'author': self.user.id,
            'name': 'Test Recipe',
            'text': 'Test Description',
            'cooking_time': 30,
            'ingredients': [
                {'id': self.ingredient.id, 'amount': 100}
            ],
            'tags': [self.tag.id],
        }
        response = self.client.post('/api/recipes/', data=data, format='json')
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['text'], data['text'])
        self.assertEqual(response.data['cooking_time'], data['cooking_time'])
