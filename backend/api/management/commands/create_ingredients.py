import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов из JSON-файла'

    def handle(self, *args, **kwargs):
        file_path = settings.INGREDIENTS_JSON_PATH
        if not os.path.exists(file_path):
            self.stderr.write(
                self.style.ERROR(f'Файл по пути {file_path} не найден.')
            )
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                ingredient, created = Ingredient.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Ингредиент {ingredient.name} добавлен.'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Ингредиент {ingredient.name} уже существует.'
                        )
                    )
