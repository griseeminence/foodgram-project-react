from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers

from recipes.models import Recipe, Tag, Ingredient, FavoriteRecipe, ShoppingCart, Subscribe


User = get_user_model()

USERNAME_MAX_LEN = 150
EMAIL_MAX_LEN = 254
username_validator = UnicodeUsernameValidator()

class UsersSerializer(serializers.ModelSerializer):
    """Сериализатор для модели CustomUser."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def get_is_subscribed(self, obj):
        pass

    def create(self, validated_data):
        pass

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = '__all__'

    def validate(self, data):
        pass


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    author = UsersSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(min_value=1, max_value=32000)
    # image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'name', 'description', 'ingredients',
            'directions', 'image')
        read_only_fields = ['author']

    def create(self, validated_data):

        user = self.context['request'].user
        recipe = Recipe.objects.create(author=user, **validated_data)
        return recipe

    def update(self, instance, validated_data):
        pass

    def get_ingredients(self, obj):
        return obj.ingredients.all()

    def get_is_favorited(self, obj):
        pass

    def validate(self, data):
        pass





class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = '__all__'


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = '__all__'


class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'











#TODO: USERS SERIALIZERs






class SignUpSerializer(serializers.Serializer):
    """Сериализатор для создания объекта класса CustomUser."""

    username = serializers.CharField(
        max_length=USERNAME_MAX_LEN,
        required=True,
        validators=[username_validator],
    )
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LEN,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            'username', 'email'
        )

    def validate(self, data):
        """
        Проверка на уникальность пользователей при регистрации.
        Запрет на одинаковые поля 'username' и 'email' при регистрации.
        """
        if not User.objects.filter(
            username=data.get("username"), email=data.get("email")
        ).exists():
            if User.objects.filter(username=data.get("username")):
                raise serializers.ValidationError(
                    "Пользователь с таким 'username' уже существует"
                )

            if User.objects.filter(email=data.get("email")):
                raise serializers.ValidationError(
                    "Пользователь с таким 'email' уже существует"
                )
        return data


class UserGetTokenSerializer(serializers.Serializer):
    """Сериализатор класса CustomUser при получении JWT."""
    username = serializers.RegexField(
        regex=r'[\w.@+-]+',
        max_length=150,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=150,
        required=True
    )

    class Meta:
        model = User
        fields = '__all__'
