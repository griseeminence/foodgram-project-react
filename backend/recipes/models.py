from django.db import models

from backend.users.models import User


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='recipes/')  # TODO: Куда аплоадим-то?
    description = models.TextField()
    ingredients = models.ManyToManyField('Ingredient')
    Tag = models.ManyToManyField('Tag')
    time_to_cook = models.IntegerField()  # TODO: Добавить время в минутах


class Ingredient(models.Model):
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2) # TODO: или можно тупо в инт?
    unit = models.CharField(max_length=25)


class Tag(models.Model):
    title = models.CharField(max_length=25, unique=True)
    color = models.CharField(max_length=25, unique=True) # TODO: Добавить цвет в тегах. Специальное поле?
    slug = models.SlugField(max_length=25, unique=True)

