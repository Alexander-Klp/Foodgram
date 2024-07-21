from django.db.models import Exists, OuterRef
from django_filters.rest_framework import (
    CharFilter,
    FilterSet,
    ModelMultipleChoiceFilter,
    BooleanFilter,
)
# from django_filters import FilterSet, CharFilter, ModelMultipleChoiceFilter, BooleanFilter
from recipes.models import Ingredient, Recipe, Tag, Favorite


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
        user = self.request.user
        if user.is_authenticated:
            if value:
                return queryset.filter(shopping_cart__user=user)
            return queryset.exclude(shopping_cart__user=user)
        return queryset.none()

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user  # Assuming you have access to the request object
        if not user.is_authenticated:
            return queryset  # If the user is not authenticated, return the original queryset

        if value:
            return queryset.annotate(
                favorited=Exists(Favorite.objects.filter(
                    content_type__model='recipe',  # Ensure this matches your ContentType model name
                    object_id=OuterRef('pk'),
                    user=user
                ))
            ).filter(favorited=True)
        return queryset.annotate(
            favorited=Exists(Favorite.objects.filter(
                content_type__model='recipe',  # Ensure this matches your ContentType model name
                object_id=OuterRef('pk'),
                user=user
            ))
        ).filter(favorited=False)