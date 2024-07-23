from django.db import models
from django.core.validators import RegexValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

from users.models import User


slug_validator = RegexValidator(
    regex=r'^[-a-zA-Z0-9_]+$',
    message='Слаг должен состоять только из букв, цифр, знаков подчеркивания или тире.'
)


class Tag(models.Model):
    name = models.CharField('Название', max_length=200, unique=True)
    color = models.CharField('Цвет в HEX', max_length=7, unique=True)
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=200,
        unique=True,
        validators=[slug_validator],
        help_text='Должен состоять из букв, цифр, знака подчеркивания или тире'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единицы измерения', max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=200)
    image = models.ImageField(
        'Картинка',
        upload_to='recipe_images/',
        null=True,
        default=None
    )
    text = models.TextField('Текстовое описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        help_text='Время приготовления в минутах'
    )
    is_favorited = GenericRelation('Favorite')
    # is_in_shopping_cart = models.BooleanField(
    #     'is_in_shopping_cart',
    #     blank=True,
    #     null=True,
    #     default=False
    # )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField('Количество')

    def __str__(self):
        return f"{self.amount} - {self.ingredient.name} для {self.recipe.name}"

    class Meta:
        verbose_name = 'Игредиент для рецепта'
        verbose_name_plural = 'Игредиенты для рецепта'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'object_id', 'content_type'],
                name='unique_user_content_type_object_id'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    def __str__(self):
        return f'Пользователь - {self.user} рецепт - {self.recipe}'

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_in_shopping_cart'
            )
        ]


class Subscribe(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    subscribed_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_to',
        verbose_name='Подписан на'
    )
    
    def __str__(self):
        return (f'{self.subscriber.username}'
                f'подписан на {self.subscribed_to.username}')

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'subscribed_to'],
                name='uniqie_follow'
            )
        ]
