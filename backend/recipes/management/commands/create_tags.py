from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Стандартные теги для рецептов'

    def handle(self, *args, **kwargs):
        default_tags = [
            {"name": "Завтрак", "color": "#E26C2D", "slug": "breakfast"},
            {"name": "Обед", "color": "#2DE26C", "slug": "lunch"},
            {"name": "Ужин", "color": "#6C2DE2", "slug": "dinner"}
        ]

        for tag_data in default_tags:
            Tag.objects.create(**tag_data)

        self.stdout.write(self.style.SUCCESS(
            'Тэги успешно добавлены.'))
