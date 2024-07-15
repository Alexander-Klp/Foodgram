from django.urls import include, path
from .views import UsersViewSet
from rest_framework.routers import DefaultRouter
from api.views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
)
router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(r'users', UsersViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
