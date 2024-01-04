from rest_framework.permissions import AllowAny

from backend.api.permissions import IsAdminOrReadOnly
from backend.api.serializers import SubscribeSerializer
from backend.recipes.models import Recipe


class GetObjectMixin:
    """Миксина для удаления/добавления рецептов избранных/корзины."""

    # serializer_class = SubscribeRecipeSerializer
    serializer_class = SubscribeSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.check_object_permissions(self.request, recipe)
        return recipe


class PermissionAndPaginationMixin:
    """Миксина для списка тегов и ингридиентов."""

    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None