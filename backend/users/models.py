from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

MAX_LENGTH_CHARACTERS_1 = 150

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLES = [
    (USER, USER),
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR),
]


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
    #
    role = models.CharField(
        'Роль',
        choices=ROLES,
        default=USER,
        max_length=MAX_LENGTH_CHARACTERS_1,
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser or self.is_staff

    def __str__(self):
        return self.username