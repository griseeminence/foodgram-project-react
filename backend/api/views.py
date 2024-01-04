from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, pagination, status
from rest_framework import viewsets, permissions, serializers
from rest_framework.viewsets import ReadOnlyModelViewSet

from .filters import IngredientFilter
from .permissions import IsAdminOrReadOnly
from .serializers import RecipeSerializer, IngredientSerializer, TagSerializer, SubscriptionSerializer, \
    FavoriteRecipeSerializer, ShoppingListSerializer, UserGetTokenSerializer, UsersSerializer, SignUpSerializer, \
    SubscribeSerializer, SubscribeListSerializer
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
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            serializer = SubscribeListSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(
                Follow, user=user, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeListSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)






# TODO: D
class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


# TODO: D
class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter