from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Recipe, Tag, Ingredient, FavoriteRecipe, ShoppingCart, Subscribe, RecipeIngredients

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
        # fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password', 'id'
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
        recipe_ingredients = RecipeIngredients.objects.filter(recipe=obj)
        ingredients_data = []
        for recipe_ingredient in recipe_ingredients:
            ingredient_data = {
                'id': recipe_ingredient.ingredient.id,
                'name': recipe_ingredient.ingredient.name,
                'measurement_unit': recipe_ingredient.ingredient.measurement_unit,
                'amount': recipe_ingredient.amount,
            }
            ingredients_data.append(ingredient_data)
        return ingredients_data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()


class RecipeIngredientsWriteSerializer(ModelSerializer):
    """Сериалайзер для модели добавления ингредиентов в рецепт."""

    id = IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeWriteSerializer(ModelSerializer):
    """Сериалайзер для рецептов. Режим методов записи."""
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                  many=True)
    author = UsersSerializer(read_only=True)

    image = Base64ImageField()
    ingredients = RecipeIngredientsWriteSerializer(many=True, read_only=True)

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
            raise ValidationError('Поле "cooking_time" должно быть указано!')
        if value < 1:
            raise ValidationError('Значение в поле "cooking_time" должно быть больше 0!')
        return value

    def validate_image(self, value):
        if not value:
            raise ValidationError('Поле "image" не может быть пустым!')
        return value

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError({'ingredients': 'Нужен хотя бы один ингредиент!'})

        ingredients_list = []
        for item in ingredients:
            if 'id' not in item:
                raise ValidationError({'ingredients': 'Указан некорректный формат ингредиента!'})

            try:
                ingredient = Ingredient.objects.get(id=item['id'])
            except Ingredient.DoesNotExist:
                raise ValidationError({'ingredients': 'Ингредиент не существует!'})

            if ingredient in ingredients_list:
                raise ValidationError({'ingredients': 'Ингредиенты не могут повторяться!'})

            if int(item['amount']) <= 0:
                raise ValidationError({'amount': 'Количество ингредиента должно быть больше 0!'})

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
        RecipeIngredients.objects.bulk_create(
            [RecipeIngredients(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        recipe = Recipe.objects.create(**validated_data)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.get('ingredients')
        tags = validated_data.get('tags')

        instance = super().update(instance, validated_data)

        if tags is not None:
            instance.tags.clear()
            instance.tags.set(tags)
        elif 'tags' not in validated_data:
            raise ValidationError({'tags': 'Поле "tags" не может быть пустым.'})

        if ingredients_data is not None:
            instance.ingredients.clear()
            self.create_ingredients_amounts(recipe=instance, ingredients=ingredients_data)
        elif 'ingredients' not in validated_data:
            raise ValidationError({'ingredients': 'Поле "ingredients" не может быть пустым.'})

        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
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
            return Subscribe.objects.filter(user=user, author=obj).exists()
        return False

    def get_recipes(self, obj):
        limit = self.context.get('request').query_params.get('recipes_limit')
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
            subscription = Subscribe.objects.create(user=current_user, author=author)
        except IntegrityError:
            raise serializers.ValidationError("Вы уже подписаны на данного пользователя", code='unique')
        return author
