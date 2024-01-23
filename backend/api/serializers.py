from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from recipes.models import (
    Ingredient, Recipe, RecipeIngredients, Subscribe, Tag
)

User = get_user_model()


class IngredientSerializer(ModelSerializer):
    """Сериалайзер для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(ModelSerializer):
    """Сериалайзер для тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class UsersSerializer(UserSerializer):
    """Сериалайзер для пользователей."""
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscribe.objects.filter(user=user, author=obj).exists()
        return False


class UsersCreateSerializer(UserCreateSerializer):
    """Сериалайзер для создания пользователя."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Невозможно создать аккаунт с username "me!"'
            )
        return value


class RecipeReadSerializer(ModelSerializer):
    """Сериалайзер для рецептов. Режим безопасных методов."""
    tags = TagSerializer(many=True, read_only=True)
    author = UsersSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

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
            'cooking_time',
        )

    def get_ingredients(self, obj):
        recipe_ingredients = RecipeIngredients.objects.filter(
            recipe=obj
        )
        ingredients_data = []
        for recipe_ingredient in recipe_ingredients:
            ingredient_data = {
                'id': recipe_ingredient.ingredient.id,
                'name': recipe_ingredient.ingredient.name,
                'measurement_unit': recipe_ingredient.ingredient.measurement_unit,
                'amount': recipe_ingredient.amount,
            }
            ingredients_data.append(ingredient_data)
        print(f"Recipe ID: {obj.id}")
        print(f"Recipe Ingredients: {ingredients_data}")
        return ingredients_data

    def is_user_anonymous(self):
        return self.context.get('request').user.is_anonymous

    def get_is_favorited(self, obj):
        if self.is_user_anonymous():
            return False
        user = self.context.get('request').user
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        if self.is_user_anonymous():
            return False
        user = self.context.get('request').user
        return user.shopping_cart.filter(recipe=obj).exists()


class RecipeIngredientsWriteSerializer(ModelSerializer):
    """Сериалайзер для модели добавления ингредиентов в рецепт."""
    id = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')

    def get_id(self, instance):
        return instance.ingredient.id


class RecipeWriteSerializer(ModelSerializer):
    """Сериалайзер для рецептов. Режим методов записи."""
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UsersSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = RecipeIngredientsWriteSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_cooking_time(self, value):
        if value is None:
            raise ValidationError(
                'Поле "cooking_time" должно быть указано!'
            )
        if value < 1:
            raise ValidationError(
                'Значение в поле "cooking_time" должно быть больше 0!'
            )
        return value

    def validate_image(self, value):
        if not value:
            raise ValidationError('Поле "image" не может быть пустым!')
        return value

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError(
                {'ingredients': 'Нужен хотя бы один ингредиент!'}
            )

        ingredients_list = []

        for item in ingredients:
            if 'id' not in item:
                raise ValidationError(
                    {'ingredients': 'Указан некорректный формат ингредиента!'}
                )

            try:
                ingredient = Ingredient.objects.get(id=item['id'])
            except Ingredient.DoesNotExist:
                raise ValidationError(
                    {'ingredients': 'Ингредиент не существует!'}
                )

            if ingredient in ingredients_list:
                raise ValidationError(
                    {'ingredients': 'Ингредиенты не могут повторяться!'}
                )

            if int(item['amount']) <= 0:
                raise ValidationError(
                    {'amount': 'Количество ингредиента должно быть больше 0!'}
                )

            ingredients_list.append(ingredient)

        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError({'tags': 'Нужно выбрать хотя бы один тег!'})
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError({'tags': 'Теги должны быть уникальными!'})
            tags_list.append(tag)
        return value

    def create_ingredients_amounts(self, ingredients, recipe):
        instances = [
            RecipeIngredients(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        for instance in instances:
            instance.save()

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])
        user = self.context['request'].user
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags_data)
        RecipeIngredients.objects.bulk_create([
            RecipeIngredients(
                ingredient=Ingredient.objects.get(id=ingredient_data['id']),
                recipe=recipe,
                amount=ingredient_data['amount']
            ) for ingredient_data in ingredients_data
        ])

        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients_amounts(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        print(f"Recipe ID: {instance.id}")
        print(f"Recipe Ingredients: {instance.ingredients.all()}")
        return RecipeReadSerializer(instance, context=context).data


class RecipeShortSerializer(ModelSerializer):
    """Сериалайзер для рецептов. Режим краткого ответа на запрос."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeSerializer(UsersSerializer):
    """Сериалайзер для логики подписок."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscribe.objects.filter(
                user=user,
                author=obj
            ).exists()
        return False

    def get_recipes(self, obj):
        limit = self.context.get(
            'request'
        ).query_params.get('recipes_limit')
        if limit:
            queryset = Recipe.objects.filter(
                author=obj).order_by('-id')[:int(limit)]
        else:
            queryset = Recipe.objects.filter(author=obj)

        return RecipeShortSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def create(self, validated_data):
        request = self.context.get('request')
        author_id = self.context['view'].kwargs.get('user_id')
        current_user = request.user
        author = get_object_or_404(User, pk=author_id)

        try:
            Subscribe.objects.create(
                user=current_user,
                author=author
            )
        except IntegrityError:
            raise serializers.ValidationError(
                'Вы уже подписаны на данного пользователя',
                code='unique'
            )
        return author
