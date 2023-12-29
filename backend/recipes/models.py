from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


# TODO: Добавить verbose_name к полям во всех моделях

class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes', verbose_name='Автор') #SET_NULL???
    name = models.CharField('Название рецепта', max_length=255)
    image = models.ImageField(
        'Изображение рецепта',
        upload_to='static/recipe/',
        blank=True,
        null=True)
    text = models.TextField('Описание рецепта', max_length=1000)
    cooking_time = models.IntegerField(verbose_name='Время приготовления', default=0)  # TODO: Добавить время в минутах
    ingredients = models.ManyToManyField('Ingredient', blank=False, through='RecipeIngredients')
    tags = models.ManyToManyField('Tag')
    pub_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['name']  # ordering = ['-created_at']

    def add_to_favorites(self, user):
        FavoriteRecipe.objects.get_or_create(user=user, recipe=self)

    def remove_from_favorites(self, user):
        FavoriteRecipe.objects.filter(user=user, recipe=self).delete()

    def is_favorited_by(self, user):
        return FavoriteRecipe.objects.filter(user=user, recipe=self).exists()

    def __str__(self):
        return f'{self.name}. Автор: {self.author.username}'


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredient')
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE, related_name='ingredient_recipe')
    amount = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Количество',)

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ['-id']


class Ingredient(models.Model):
    name = models.CharField('Название ингредиента', max_length=100)
    measurement_unit = models.CharField('Единица измерения', max_length=25)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Tag(models.Model):
    name = models.CharField('Название', max_length=25, unique=True)
    color = models.CharField('Цвет', max_length=25,
                             unique=True, db_index=False)  # TODO: Добавить цвет в тегах. Специальное поле?
    slug = models.SlugField('Слаг', max_length=25, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['-id']

    def __str__(self):
        return f'{self.name} (цвет: {self.color})'



class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор')
    created_at = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-id']

    def __str__(self):
        return f'Пользователь {self.user} -> автор {self.author}'


class ShoppingCart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        null=True,
        verbose_name='Пользователь')
    recipe = models.ManyToManyField(
        Recipe,
        related_name='shopping_cart',
        verbose_name='Покупка')
    date_added = models.DateTimeField(
        verbose_name="Дата добавления", auto_now_add=True, editable=False
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        ordering = ['-id']

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"

class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"


    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"