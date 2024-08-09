from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


class ManageListMixin:
    """
    Общий миксин для добавления и удаления рецептов в списках
    (избранное, корзина покупок и т.д.).
    """

    def add_to_list(self, request, model_class, serializer_class, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if model_class.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            return Response(
                {'error': 'Рецепт уже добавлен в список'},
                status=status.HTTP_400_BAD_REQUEST
            )

        obj, created = model_class.objects.get_or_create(
            user=request.user,
            recipe=recipe)
        serializer = serializer_class(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_from_list(self, request, model_class, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if not model_class.objects.filter(
                user=request.user,
                recipe=recipe
        ).exists():
            return Response(
                {'error': 'У вас нет рецепта'},
                status=status.HTTP_400_BAD_REQUEST)
        obj = get_object_or_404(model_class, user=request.user, recipe=recipe)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
