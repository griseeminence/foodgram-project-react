from django.contrib import admin

from .models import Recipe, Ingredient, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    # list_editable = ('title', 'author')
    search_fields = ('name',)

    def author_name(self, obj):
        return obj.author.username

    def favorites_count(self, obj):
        return obj.favorite_recipes.count()

    # TODO: Не понял, как это реализовать: на странице рецепта вывести общее число добавлений этого рецепта в избранное;


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    # list_editable = ('title', 'amount', 'unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    # list_editable = ('title', 'color', 'slug')
    search_fields = ('name',)
