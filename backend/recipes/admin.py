from django.contrib import admin

from .models import Recipe, Ingredient, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author')
    list_filter = ('author', 'title', 'tag')
    list_editable = ('title', 'author')
    search_fields = ('title',)

    def author_name(self, obj):
        return obj.author.username

    def favorites_count(self, obj):
        return obj.favorite_recipes.count()

    # TODO: Не понял, как это реализовать: на странице рецепта вывести общее число добавлений этого рецепта в избранное;


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit')
    list_filter = 'title'
    list_editable = ('title', 'amount', 'unit')
    search_fields = ('title',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('title', 'color', 'slug')
    list_editable = ('title', 'color', 'slug')
    search_fields = ('title',)
