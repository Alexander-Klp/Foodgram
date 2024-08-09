from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscribe,
    Tag,
)


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ['subscriber',
                    'subscribed_to']


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Админ-панель для модели "Избранное".
    """
    list_display = ('user', 'recipe', '__str__')
    list_filter = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    ordering = ('-id',)
    raw_id_fields = ('user', 'recipe')


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    fields = ('ingredient', 'amount')
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time', 'favorite_count')
    search_fields = ('author__username', 'name', 'tags__name')
    list_filter = ('author', 'name', 'tags')
    inlines = [RecipeIngredientInline]
    empty_value_display = '-пусто-'
