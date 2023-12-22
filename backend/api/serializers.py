from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers

from backend.recipes.models import Recipe, Tag, Ingredient
from backend.users.models import User

USERNAME_MAX_LEN = 150
EMAIL_MAX_LEN = 254
username_validator = UnicodeUsernameValidator()


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""
    class Meta:
        model = Recipe
        fields = (
            'name', 'description', 'ingredients',
            'directions', 'image')

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""
    class Meta:
        model = Tag
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""
    class Meta:
        model = Ingredient
        fields = '__all__'

















# def not_me_validator(value):
#     """
#     Запрет на 'me' в поле 'username'.
#     """
#     if value.lower() == "me":
#         raise ValidationError(
#             "Ошибка: запрет на 'me' в поле 'username'"
#         )
#
# class UsersSerializer(serializers.ModelSerializer):
#     """Сериализатор для модели CustomUser."""
#
#     class Meta:
#         model = User
#         fields = (
#             'username', 'email', 'first_name',
#             'last_name', 'bio', 'role')
#
#
# class SignUpSerializer(serializers.Serializer):
#     """Сериализатор для создания объекта класса CustomUser."""
#
#     username = serializers.CharField(
#         max_length=USERNAME_MAX_LEN,
#         required=True,
#         validators=[not_me_validator, username_validator],
#     )
#     email = serializers.EmailField(
#         max_length=EMAIL_MAX_LEN,
#         required=True,
#     )
#
#     class Meta:
#         model = User
#         fields = (
#             'username', 'email'
#         )
#
#     def validate(self, data):
#         """
#         Проверка на уникальность пользователей при регистрации.
#         Запрет на одинаковые поля 'username' и 'email' при регистрации.
#         """
#         if not User.objects.filter(
#             username=data.get("username"), email=data.get("email")
#         ).exists():
#             if User.objects.filter(username=data.get("username")):
#                 raise serializers.ValidationError(
#                     "Пользователь с таким 'username' уже существует"
#                 )
#
#             if User.objects.filter(email=data.get("email")):
#                 raise serializers.ValidationError(
#                     "Пользователь с таким 'email' уже существует"
#                 )
#         return data
#
#
# class UserGetTokenSerializer(serializers.Serializer):
#     """Сериализатор класса CustomUser при получении JWT."""
#     username = serializers.RegexField(
#         regex=r'[\w.@+-]+',
#         max_length=150,
#         required=True
#     )
#     confirmation_code = serializers.CharField(
#         max_length=150,
#         required=True
#     )
#
#     class Meta:
#         model = User
#         fields = '__all__'