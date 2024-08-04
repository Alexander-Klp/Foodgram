from http import HTTPStatus

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from recipes.models import Ingredient, Tag
from users.models import User


class RecipesAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.ingredient1 = Ingredient.objects.create(
            name='Ingredient 1',
            measurement_unit='g'
        )
        self.ingredient2 = Ingredient.objects.create(
            name='Ingredient 2',
            measurement_unit='ml'
        )
        self.tag1 = Tag.objects.create(
            name='Tag 1',
            color='#FF5733',
            slug='tag-1'
        )
        self.tag2 = Tag.objects.create(
            name='Tag 2',
            color='#33FF57',
            slug='tag-2'
        )

    # def test_create_recipe(self):
    #     data = {
    #         "ingredients": [
    #             {"id": self.ingredient1.id, "amount": 100},  # type: ignore
    #             {"id": self.ingredient2.id, "amount": 200}  # type: ignore
    #         ],
    #         "tags": [self.tag1.id, self.tag2.id],   # type: ignore
    #         "image": (
    #             "data:image/png;base64,"
    #             "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAg"
    #             "MAAABieywaAAAACVBMVEUAAAD///9fX1/"
    #             "S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bA"
    #             "AAACklEQVQImWNoAAAAggCByxOyYQAAAAB"
    #             "JRU5ErkJggg=="
    #         ),
    #         "name": "Еще одна попытка приготовить еду",
    #         "text": "Вероятно стоит это смешать.",
    #         "cooking_time": 10
    #     }
    #     response = self.client.post('/api/recipes/', data, format='json')
    #     if response.status_code != HTTPStatus.CREATED:
    #         print("Errors:", response.data)   # type: ignore
    #     self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_list_exists(self):
        """Проверка доступности списка рецептов."""
        response = self.client.get('/api/recipes/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_download_shopping_cart(self):
        """Проверка недоступности скачивания списка покупок."""
        self.client.force_authenticate(user=None)  # type: ignore
        response = self.client.get('/api/recipes/download_shopping_cart/')
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
