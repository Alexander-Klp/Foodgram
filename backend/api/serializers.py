from collections import Counter

from django.contrib.contenttypes.models import ContentType
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from api.fields import Base64ImageField
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscribe,
    Tag,
)
from users.models import User


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Сериализатор создания кастомного пользователя.
    """
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        required=True,
        max_length=128,
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password'
        )


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор кастомного пользователя.
    """
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscribe.objects.filter(
                subscriber=request.user,
                subscribed_to=obj
            ).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Tags.
    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient.
    """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор RecipeIngredient для просмотра рецепта
    """
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для GET запросов Рецепта.
    """
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipeingredient_set'
    )
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(
                user=user,
                content_type=ContentType.objects.get_for_model(Recipe),
                object_id=obj.id
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        return False

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор RecipeIngredient для создания рецепта.
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиентов должно быть больше чем 1.'
            )
        return value


class RecipeCreateSerializer(RecipeSerializer):
    """
    Сериализатор создания рецепта.
    """
    ingredients = RecipeIngredientCreateSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField(allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def to_representation(self, obj):
        self.fields.pop('ingredients')
        representation = super().to_representation(obj)
        representation['ingredients'] = RecipeIngredientSerializer(
            RecipeIngredient.objects.filter(recipe=obj).all(), many=True
        ).data
        tags = obj.tags.all()
        tags_representation = TagSerializer(tags, many=True).data
        representation['tags'] = tags_representation
        return representation

    def validate(self, data):
        if not data.get('ingredients'):
            raise serializers.ValidationError('Нет ингредиентов')
        if not data.get('tags'):
            raise serializers.ValidationError('Нет тэгов')
        if data['cooking_time'] < 1:
            raise serializers.ValidationError(
                'Количество ингредиентов должно быть больше чем 1.'
            )
        ingredients_data = data.get('ingredients', [])
        ingredient_ids = [
            ingredient['id'].id
            for ingredient in ingredients_data
        ]
        ingredient_counts = Counter(ingredient_ids)
        for count_ingr in ingredient_counts.values():
            if count_ingr > 1:
                raise serializers.ValidationError('Ингредиенты дублируются.')
        tags_data = data.get('tags', [])
        tags_count = Counter(tags_data)
        for count_tags in tags_count.values():
            if count_tags > 1:
                raise serializers.ValidationError('Тэги дублируются.')
        return data

    def recipe_ingredients(self, instance, ingredients_data):
        ingredients = [
            RecipeIngredient(
                recipe=instance,
                ingredient_id=ingredient_data['id'].id,
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]
        return RecipeIngredient.objects.bulk_create(ingredients)

    def create(self, validated_data):
        author = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.recipe_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients_data = validated_data.pop('ingredients')
        self.recipe_ingredients(instance, ingredients_data)
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.save()
        return super().update(instance, validated_data)


class RecipeSubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Recipe с ограниченным набором полей.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteRecipeSerializer(RecipeSerializer):
    """
    Сериализатор для вывода упрощенной информации о рецепте.
    """
    class Meta(RecipeSerializer.Meta):
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(CustomUserSerializer):
    """
    Сериализатор для модели Подписки.
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )
        read_only_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
        )
        recipe_user = Recipe.objects.filter(author=obj)

        if recipes_limit is not None:
            recipe_user = recipe_user[:int(recipes_limit)]

        serializer = RecipeSubscriptionSerializer(
            recipe_user,
            many=True,
            context=self.context
        )
        return serializer.data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ShoppingCart.
    """
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = ('__all__')
