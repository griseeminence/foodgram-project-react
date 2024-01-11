
from django.db.models import Sum
from django.http import HttpResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.authentication import SessionAuthentication
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
import datetime
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import IngredientSerializer, TagSerializer, RecipeReadSerializer, RecipeWriteSerializer, \
    RecipeShortSerializer, UsersSerializer, SubscribeSerializer
from recipes.models import Recipe, Tag, Ingredient, FavoriteRecipe, ShoppingCart, Subscribe, RecipeIngredients

from django.contrib.auth import get_user_model

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, AllowAny, IsAuthenticatedOrReadOnly

from rest_framework.response import Response

from recipes.models import RecipeIngredients

User = get_user_model()

class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

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

        # Проверяем, есть ли уже рецепт в корзине пользователя
        existing_entry = model.objects.filter(user=user, recipe=recipe).first()
        if existing_entry:
            return Response({'errors': 'Рецепт уже добавлен в корзину!'}, status=status.HTTP_400_BAD_REQUEST)

        # Если рецепта ещё нет в корзине, то добавляем
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален или не существует'}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)


        return


# class RecipeViewSet(ModelViewSet):
#     queryset = Recipe.objects.all()
#     permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
#     pagination_class = CustomPagination
#     filter_backends = (DjangoFilterBackend,)
#     filterset_class = RecipeFilter
#
#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user)
#
#     def get_serializer_class(self):
#         if self.request.method in SAFE_METHODS:
#             return RecipeReadSerializer
#         return RecipeWriteSerializer
#
#     @action(
#         detail=True,
#         methods=['post', 'delete'],
#         permission_classes=[IsAuthenticated]
#     )
#     def favorite(self, request, pk):
#         if request.method == 'POST':
#             return self.add_to(FavoriteRecipe, request.user, pk)
#         else:
#             return self.delete_from(FavoriteRecipe, request.user, pk)
#
#     @action(
#         detail=True,
#         methods=['post', 'delete'],
#         permission_classes=[IsAuthenticated]
#     )
#     def shopping_cart(self, request, pk):
#         if request.method == 'POST':
#             return self.add_to(ShoppingCart, request.user, pk)
#         else:
#             return self.delete_from(ShoppingCart, request.user, pk)
#
#     def add_to(self, model, user, pk):
#         recipe = get_object_or_404(Recipe, id=pk)
#
#         # Проверяем, есть ли уже рецепт в корзине пользователя
#         existing_entry = model.objects.filter(user=user, recipe=recipe).first()
#         if existing_entry:
#             return Response({'errors': 'Рецепт уже добавлен в корзину!'}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Если рецепта ещё нет в корзине, то добавляем
#         model.objects.create(user=user, recipe=recipe)
#         serializer = RecipeShortSerializer(recipe)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#     def delete_from(self, model, user, pk):
#         obj = model.objects.filter(user=user, recipe__id=pk)
#         if obj.exists():
#             obj.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response({'errors': 'Рецепт уже удален!'}, status=status.HTTP_400_BAD_REQUEST)
#
#     @action(
#         detail=False,
#         permission_classes=[IsAuthenticated]
#     )
#     def download_shopping_cart(self, request):
#         user = request.user
#         if not user.shopping_cart.exists():
#             return Response(status=HTTP_400_BAD_REQUEST)
#
#         ingredients = RecipeIngredients.objects.filter(
#             recipe__shopping_cart__user=request.user
#         ).values(
#             'ingredient__name',
#             'ingredient__measurement_unit'
#         ).annotate(amount=Sum('amount'))
#
#         today = datetime.today()
#         shopping_list = (
#             f'Список покупок для: {user.get_full_name()}\n\n'
#             f'Дата: {today:%Y-%m-%d}\n\n'
#         )
#         shopping_list += '\n'.join([
#             f'- {ingredient["ingredient__name"]} '
#             f'({ingredient["ingredient__measurement_unit"]})'
#             f' - {ingredient["amount"]}'
#             for ingredient in ingredients
#         ])
#         shopping_list += f'\n\nFoodgram ({today:%Y})'
#
#         filename = f'{user.username}_shopping_list.txt'
#         response = HttpResponse(shopping_list, content_type='text/plain')
#         response['Content-Disposition'] = f'attachment; filename={filename}'
#
#         return response

#TODO: D
class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]


    @action(detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


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
            serializer = SubscribeSerializer(author,
                                             data=request.data,
                                             context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(Subscribe,
                                             user=user,
                                             author=author)
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
        serializer = SubscribeSerializer(pages,
                                         many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)




# TODO: D
class IngredientViewSet(ReadOnlyModelViewSet):

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = [AllowAny, ]
    pagination_class = None

    filter_backends = [IngredientFilter, ]
    search_fields = ['^name', ]


class TagViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    permission_classes = [AllowAny, ]
    pagination_class = None
