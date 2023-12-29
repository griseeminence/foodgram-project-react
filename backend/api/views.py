from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render
from rest_framework import viewsets, pagination, status
from rest_framework import viewsets, permissions, serializers
from .serializers import RecipeSerializer, IngredientSerializer, TagSerializer, SubscriptionSerializer, \
    FavoriteRecipeSerializer, ShoppingListSerializer, UserGetTokenSerializer, UsersSerializer, SignUpSerializer
from recipes.models import Recipe, Tag, Ingredient, FavoriteRecipe, ShoppingCart, Subscribe
from rest_framework.decorators import action

from django.conf import settings
from django.contrib.auth import get_user_model

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from django.shortcuts import render

from rest_framework.response import Response



User = get_user_model()

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = pagination.PageNumberPagination

    def perform_create(self, serializer):
        # Метод perform_create используется для дополнительных действий при создании объекта
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # Добавим проверку владения рецептом
        recipe = self.get_object()
        if recipe.author == self.request.user:
            serializer.save()
        else:
            raise permissions.PermissionDenied("You do not have permission to edit this recipe.")

    def perform_destroy(self, instance):
        # Добавим проверку владения рецептом
        if instance.author == self.request.user:
            instance.delete()
        else:
            raise permissions.PermissionDenied("You do not have permission to delete this recipe.")

    def get_queryset(self):
        return Recipe.objects.order_by(
            '-created_at')  # Есть сортировка в самой модели. Нужна ли она здесь? Не будет ли конфликтов?

    @action(detail=True, methods=['post'])
    def add_to_favorites(self, request, pk=None):
        recipe = self.get_object()
        serializer = FavoriteRecipeSerializer(data={'user': request.user.id, 'recipe': recipe.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Recipe added to favorites successfully.'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_to_shopping_list(self, request, pk=None):
        recipe = self.get_object()
        serializer = ShoppingListSerializer(data={'user': request.user.id, 'recipe': recipe.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Recipe added to shopping list successfully.'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def subscribe_to_author(self, request, pk=None):
        recipe = self.get_object()
        author = recipe.author
        serializer = SubscriptionSerializer(data={'user': request.user.id, 'author': author.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Subscribed to author successfully.'}, status=status.HTTP_201_CREATED)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    # filter_backends = [IngredientSearchFilter]


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscribe.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        author = serializer.validated_data['author']
        if self.request.user == author:
            raise serializers.ValidationError("You cannot subscribe to yourself.")
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Subscribe.objects.filter(user=self.request.user)


class FavoriteRecipeViewSet(viewsets.ModelViewSet):
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return FavoriteRecipe.objects.filter(user=self.request.user)


class ShoppingListViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def download_shopping_list(self, request):
        pass


def send_conf_code(email, confirmation_code):
    """Дополнительная функция для SignupViewSet."""
    send_mail(
        subject='Регистрация на сайте Yamdb.com',
        message=f'Код подтверждения: {confirmation_code}',
        from_email=settings.TEST_EMAIL,
        recipient_list=(email,)
    )


class SignupViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """ViewSet регистрации нового пользователя."""
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (AllowAny,)

    def create(self, request):
        """Создаем пользователя (CustomUser), затем высылаем
        код подтверждение на e-mail в профиле."""

        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, _ = User.objects.get_or_create(**serializer.validated_data)
        confirmation_code = default_token_generator.make_token(user)

        send_conf_code(
            email=user.email,
            confirmation_code=confirmation_code
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    """Вьюсет для обьектов модели User."""

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        detail=False,
        methods=['get', 'patch', 'delete'],
        url_path=r'([\w.@+-]+)',
        url_name='get_user',
        permission_classes=(IsAuthenticated,)
    )
    def get_username_info(self, request, username):
        """
        Получает информацию о пользователе по полю 'username'
        с возможность редактирования.
        """
        user = get_object_or_404(User, username=username)
        if request.method == 'PATCH':
            serializer = UsersSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = UsersSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        url_name='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_data_for_me(self, request):
        """Получает информацию о себе с возможностью
        частичного изменения через patch."""
        if request.method == 'PATCH':
            serializer = UsersSerializer(
                request.user,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UsersSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Получение JWT токена с проверкой."""
    queryset = User.objects.all()
    serializer_class = UserGetTokenSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = UserGetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            message = {'confirmation_code': 'Неверный код подтверждения'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        message = {'token': str(AccessToken.for_user(user))}
        return Response(message, status=status.HTTP_200_OK)
