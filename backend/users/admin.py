from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_filter = ('email', 'first_name')
    list_display = (
        'email',
        'first_name',
        'last_name',
        'id',
        'username',
    )
