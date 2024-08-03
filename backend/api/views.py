from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

import pyshorteners

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import RecipePagination
from api.permissions import AuthorOrReadOnly
from api.serializers import (
    CustomUserSerializer,
    FavoriteRecipeSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeIngredient,
    RecipeSerializer,
    RecipeSubscriptionSerializer,
    SubscribeSerializer,
    TagSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscribe,
    Tag,
)
from users.models import User

from .create_pdf import generate_shopping_cart_pdf


class ManageFavorite:
    """
    Класс миксин для добавление или удаления рецепта из "Избранного"
    эндпоинт api/recipes/{id}/favorite/
    """
    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        try:
            instance = self.get_object()  # type: ignore
        except Http404:
            return Response(
                {'error': 'Рецепт не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        content_type = ContentType.objects.get_for_model(instance)
        if request.method == 'POST':
            favorite_obj, created = Favorite.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=instance.id
            )
            if created:
                serializer = FavoriteRecipeSerializer(instance)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'error': 'Рецепт уже находится в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            try:
                favorite_obj = Favorite.objects.get(
                    user=request.user,
                    content_type=content_type,
                    object_id=instance.id
                )
                favorite_obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Favorite.DoesNotExist:
                return Response(
                    {'error': 'Рецепт не находится в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )


class UsersViewSet(UserViewSet):
    """
    ViewSet для эндпоинта api/users/
    """
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False,
            methods=['get'],
            permission_classes=(permissions.IsAuthenticated,),
            url_path='subscriptions',
            )
    def subscriptions(self, request):
        """
        Функция для эндпоинта /api/users/subscriptions/
        """
        user = request.user
        user_subscriptions = Subscribe.objects.filter(subscriber=user)
        subscribed_users = [
            subscription.subscribed_to for subscription in user_subscriptions
        ]
        serializer = SubscribeSerializer(
            subscribed_users, many=True, context={'request': request}
        )
        page = self.paginate_queryset(serializer.data)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(serializer.data)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,),
            url_path='subscribe',
            )
    def subscribe(self, request, id=None):
        """
        Функция для эндпоинта /api/users/{Id}/subscribe/
        """
        subscribed_to = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if request.user == subscribed_to:
                return Response(
                    {'error': 'Вы не можете на самого себя подписаться'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscribe.objects.filter(
                subscriber=request.user,
                subscribed_to=subscribed_to
            ).exists():
                return Response(
                    {'error': 'У вас уже есть подписка на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user_sub, _ = Subscribe.objects.get_or_create(
                subscriber=request.user,
                subscribed_to=subscribed_to
            )
            serializer = SubscribeSerializer(
                subscribed_to,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not Subscribe.objects.filter(
                subscriber=request.user,
                subscribed_to=subscribed_to
            ).exists():
                return Response(
                    {'error': 'У вас нет подписки на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription = get_object_or_404(
                Subscribe,
                subscriber=request.user,
                subscribed_to=subscribed_to
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['put', 'patch', 'delete'],
            permission_classes=(permissions.IsAuthenticated,),
            url_path='me/avatar')
    def avatar(self, request):
        """
        Функция для эндпоинта /api/users/me/avatar/
        """
        user = request.user
        if request.method == 'PUT' or request.method == 'PATCH':
            if 'avatar' not in request.data:
                return Response(
                    {'detail': 'Нужна картинка для аватара.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = CustomUserSerializer(
                user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                avatar_url = serializer.data.get('avatar', '')  # type: ignore
                return Response(
                    {'avatar': avatar_url},
                    status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == 'DELETE':
            user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet для эндпоинта /api/tags/
    """
    http_method_names = ['get']
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """
    ViewSet для эндпоинта /api/ingredients/
    """
    http_method_names = ['get']
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet, ManageFavorite):
    """
    ViewSet для эндпоинта /api/recipes/
    """
    queryset = Recipe.objects.all().order_by('-pub_date')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = (AuthorOrReadOnly,)
        return super().get_permissions()

    @action(detail=False,
            methods=['get'],
            permission_classes=(permissions.IsAuthenticated,),
            url_path='download_shopping_cart',
            )
    def download_shopping_cart(self, request):
        """
        Функция для эндпоинта /api/recipes/download_shopping_cart/.
        Создает файл PDF со всеми ингредиентами добавленными в список покупок.
        """
        user = request.user
        shopping_cart_recipes = Recipe.objects.filter(shopping_cart__user=user)

        if not shopping_cart_recipes.exists():
            return Response(
                {'error': 'Нет в корзине рецептов'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ingredients = RecipeIngredient.objects.filter(
            recipe__in=shopping_cart_recipes
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))

        return generate_shopping_cart_pdf(ingredients)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,),
            url_path='shopping_cart',
            )
    def shopping_cart(self, request, pk=None):
        """
        Функция для эндпоинта /api/recipes/{id}/shopping_cart/
        """
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(id=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {'error': 'Нет такого рецепта'},
                    status=status.HTTP_404_NOT_FOUND
                )
            if ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'error': 'Рецепт уже добавлен'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe_in_cart, _ = ShoppingCart.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            serializer = RecipeSubscriptionSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            if not ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'error': 'У вас нет рецепта в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            in_shopping_cart = get_object_or_404(
                ShoppingCart,
                user=request.user,
                recipe=recipe
            )
            in_shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['get'],
            url_path='get-link',
            )
    def get_link(self, request, pk=None):
        """
        Функция для эндпоинта /api/recipes/{id}/get-link/
        """
        try:
            _ = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            return Response(
                {'error': 'Несуществующий рецепт'},
                status=status.HTTP_404_NOT_FOUND
            )
        original_link = request.build_absolute_uri(f'/api/recipes/{pk}/')
        s = pyshorteners.Shortener()
        short_link = s.tinyurl.short(original_link)
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)
