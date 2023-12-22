from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    list_edit = (
        'first_name',
        'last_name',
    )
    search_fields = (
        'email',
        'username',
    )
