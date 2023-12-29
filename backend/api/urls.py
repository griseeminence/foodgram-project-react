from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, TagViewSet, IngredientViewSet, SubscriptionViewSet, FavoriteRecipeViewSet, \
    ShoppingListViewSet, UsersViewSet

app_name = 'api'

router = DefaultRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'favorite-recipes', FavoriteRecipeViewSet, basename='favorite-recipe')
router.register(r'shopping-list', ShoppingListViewSet, basename='shopping-list')
router.register("users", UsersViewSet, "users")

urlpatterns = [
    path('', include(router.urls)),
    # path('', something.as_view(), name='home'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
