
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, TagViewSet, IngredientViewSet, UsersViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', UsersViewSet)
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
