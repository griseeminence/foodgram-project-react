from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, TagViewSet, IngredientViewSet, UsersViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', UsersViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]


# router_v1 = DefaultRouter()
# router_v1.register('users', UsersViewSet, basename='users')
# router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
# router_v1.register('tags', TagViewSet, basename='tags')
# router_v1.register('recipes', RecipeViewSet, basename='recipes')
#
#
# urlpatterns = [
#     path('', include(router_v1.urls)),
#     path('', include('djoser.urls')),
#     path('auth/', include('djoser.urls.authtoken')),
# ]
