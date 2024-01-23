from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredients, ShoppingCart, Subscribe, Tag)

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeShortSerializer, RecipeWriteSerializer,
                          SubscribeSerializer, TagSerializer, UsersSerializer)

User = get_user_model()


class RecipeViewSet(ModelViewSet):
    """Вьюсет для рецептов и операций с ними."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            if 'ingredients' in e.get_full_details():
                return Response(
                    {'error': 'Bad Request: Поле "ingredients" пустое.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {'error': 'Bad Request'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)
        recipe = serializer.instance
        ingredients_data = request.data.get('ingredients', [])

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            amount = ingredient_data.get('amount')
            if ingredient_id and amount:
                ingredient = Ingredient.objects.get(pk=ingredient_id)
                RecipeIngredients.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount
                )

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        tags_data = request.data.get('tags', [])
        instance.tags.set(tags_data)

        ingredients_data = request.data.get('ingredients', [])
        ingredients_to_delete = [
            ingredient['id'] for ingredient in instance.ingredients.values()
        ]

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            amount = ingredient_data.get('amount')

            recipe_ingredient, created = RecipeIngredients.objects.get_or_create(
                recipe=instance,
                ingredient_id=ingredient_id,
                defaults={'amount': amount}
            )

            if not created:
                recipe_ingredient.amount = amount
                recipe_ingredient.save()

            if ingredient_id in ingredients_to_delete:
                ingredients_to_delete.remove(ingredient_id)

        RecipeIngredients.objects.filter(
            recipe=instance,
            ingredient_id__in=ingredients_to_delete
        ).delete()

        self.perform_update(serializer)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(FavoriteRecipe, request.user, pk)
        else:
            return self.delete_from(FavoriteRecipe, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(ShoppingCart, request.user, pk)
        else:
            return self.delete_from(ShoppingCart, request.user, pk)

    def add_to(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        existing_entry = model.objects.filter(
            user=user,
            recipe=recipe
        ).first()
        if existing_entry:
            return Response(
                {'errors': 'Рецепт уже добавлен в корзину!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = get_object_or_404(model, user=user, recipe__id=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        def get_user_shopping_cart_ingredients():
            return RecipeIngredients.objects.filter(
                recipe__shopping_cart__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
            )

        def aggregate_ingredient_amount(ingredients):
            return ingredients.annotate(amount=Sum('amount'))

        def format_ingredient_line(ingredient):
            return (
                f'- {ingredient["ingredient__name"]}'
                f'({ingredient["ingredient__measurement_unit"]})'
                f'- {ingredient["amount"]}'
            )

        user_ingredients = get_user_shopping_cart_ingredients()
        aggregated_ingredients = aggregate_ingredient_amount(user_ingredients)
        name = f'shopping_list_for_{user.get_username}.txt'
        shopping_list = f'Что купить для {user.get_username()}:\n'
        shopping_list += '\n'.join(
            [format_ingredient_line(ingredient) for ingredient in aggregated_ingredients]
        )

        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={name}'

        return response


class UsersViewSet(UserViewSet):
    """Вьюсет для пользователей и подписок."""
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = CustomPagination
    permission_classes = (AllowAny,)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)

        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author,
                data=request.data,
                context={"request": request}
            )
            try:
                serializer.is_valid(raise_exception=True)
                Subscribe.objects.create(user=user, author=author)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            except IntegrityError:
                return Response(
                    {'detail': 'Уже подписан.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscribe,
                user=user,
                author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    search_fields = ['^name', ]
    filter_backends = [IngredientFilter, ]


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None
