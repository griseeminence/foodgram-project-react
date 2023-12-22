from django.db import models

from backend.users.models import User

#TODO: Добавить verbose_name к полям во всех моделях

class Recipe(models.Model):
    title = models.CharField('Название', max_length=100)
    image = models.ImageField('Изображение', upload_to='recipes/')  # TODO: Куда аплоадим-то?
    description = models.TextField('Описание', max_length=1000)
    time_to_cook = models.IntegerField(verbose_name='Время приготовления')  # TODO: Добавить время в минутах
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    ingredients = models.ManyToManyField('Ingredient')
    tag = models.ManyToManyField('Tag')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['title']


    def __str__(self):
        return self.title


class Ingredient(models.Model):
    title = models.CharField('Название', max_length=100)
    amount = models.DecimalField('Количество', max_digits=10, decimal_places=2) # TODO: или можно тупо в инт?
    unit = models.CharField('Единица измерения', max_length=25)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['title']

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField('Название', max_length=25, unique=True)
    color = models.CharField('Цветовой код', max_length=25, unique=True) # TODO: Добавить цвет в тегах. Специальное поле?
    slug = models.SlugField('Слаг', max_length=25, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['title']

    def __str__(self):
        return self.title