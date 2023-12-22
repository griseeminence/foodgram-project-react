from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework.routers import DefaultRouter

app_name = 'users'

router = DefaultRouter()

# router.register(
#     'users',
#     UsersViewSet,
#     basename='users'
# )

urlpatterns = [
    # path('', something.as_view(), name='home'),
]