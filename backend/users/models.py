from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models



MAX_LENGTH_CHARACTERS_1 = 150


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        'username',
        max_length=MAX_LENGTH_CHARACTERS_1,
        unique=True,
        validators=[username_validator]
    )
    first_name = models.CharField(
        'first name',
        max_length=MAX_LENGTH_CHARACTERS_1,
        blank=True
    )
    last_name = models.CharField(
        'last name',
        max_length=MAX_LENGTH_CHARACTERS_1,
        blank=True
    )
    email = models.EmailField(
        'email address',
        unique=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def subscribe(self, author):
        Subscription.objects.get_or_create(user=self, author=author)

    def unsubscribe(self, author):
        Subscription.objects.filter(user=self, author=author).delete()

    def is_subscribed_to(self, author):
        return Subscription.objects.filter(user=self, author=author).exists()

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'author')
        # models.UniqueConstraint(
        #     fields=(
        #         "user",
        #         "author",
        #     ),
        #     name="unique_follow",
        # )



