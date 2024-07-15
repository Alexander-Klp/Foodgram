from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from recipes.models import (
    Tag,
    Recipe,
    Ingredient,
    Favorite,
    RecipeIngredient,
    ShoppingCart,
    Subscribe
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
    list_display = ('user',
                    'content_type',
                    'object_id',
                    'content_object')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'content_type':
            kwargs['queryset'] = ContentType.objects.filter(model='recipe')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
    readonly_fields = ('amount',)
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time', 'get_favorite_count')
    search_fields = ('author__username', 'name', 'tags__name')
    list_filter = ('author', 'name', 'tags')
    inlines = [RecipeIngredientInline]
    empty_value_display = '-пусто-'

    def get_favorite_count(self, obj):
        return obj.is_favorited.count()

    get_favorite_count.short_description = 'Кол-во избранных'
