from django.contrib import admin
from django import forms
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


class FavoriteAdminForm(forms.ModelForm):
    content_object = forms.ModelChoiceField(queryset=Recipe.objects.all(), label='Recipe')

    class Meta:
        model = Favorite
        fields = ('user', 'content_type', 'content_object')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['content_object'] = self.instance.content_object

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.content_type = ContentType.objects.get_for_model(self.cleaned_data['content_object'])
        instance.object_id = self.cleaned_data['content_object'].id
        if commit:
            instance.save()
        return instance

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    form = FavoriteAdminForm
    list_display = ('user', 'content_type', 'object_id', 'content_object')
    
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
