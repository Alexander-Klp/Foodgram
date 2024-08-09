from django_filters.rest_framework import (
    BooleanFilter,
    CharFilter,
    FilterSet,
    ModelMultipleChoiceFilter,
)

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    author = CharFilter(field_name='author', lookup_expr='exact')
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart')
    is_favorited = BooleanFilter(method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_in_shopping_cart', 'is_favorited')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user    # type: ignore
        if user.is_authenticated:
            if value:
                return queryset.filter(shopping_cart__user=user)
            return queryset.exclude(shopping_cart__user=user)
        return queryset.none()

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user    # type: ignore
        if user.is_authenticated:
            if value:
                return queryset.filter(favorites__user=user)
            return queryset.exclude(favorites__user=user)
        return queryset.none()
