from django.shortcuts import render



























# Create your views here.
# def send_conf_code(email, confirmation_code):
#     """Дополнительная функция для SignupViewSet."""
#     send_mail(
#         subject='Регистрация на сайте Yamdb.com',
#         message=f'Код подтверждения: {confirmation_code}',
#         from_email=settings.TEST_EMAIL,
#         recipient_list=(email,)
#     )
#
#
# class SignupViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
#     """ViewSet регистрации нового пользователя."""
#     queryset = CustomUser.objects.all()
#     serializer_class = SignUpSerializer
#     permission_classes = (AllowAny,)
#
#     def create(self, request):
#         """Создаем пользователя (CustomUser), затем высылаем
#         код подтверждение на e-mail в профиле."""
#
#         serializer = SignUpSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user, _ = CustomUser.objects.get_or_create(**serializer.validated_data)
#         confirmation_code = default_token_generator.make_token(user)
#
#         send_conf_code(
#             email=user.email,
#             confirmation_code=confirmation_code
#         )
#
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#
# class UsersViewSet(mixins.ListModelMixin,
#                    mixins.CreateModelMixin,
#                    viewsets.GenericViewSet):
#     """Вьюсет для обьектов модели User."""
#
#     queryset = CustomUser.objects.all()
#     serializer_class = UsersSerializer
#     permission_classes = (IsAuthenticated, IsAdmin,)
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ('username',)
#
#     @action(
#         detail=False,
#         methods=['get', 'patch', 'delete'],
#         url_path=r'([\w.@+-]+)',
#         url_name='get_user',
#         permission_classes=(IsAdmin,)
#     )
#     def get_username_info(self, request, username):
#         """
#         Получает информацию о пользователе по полю 'username'
#         с возможность редактирования.
#         """
#         user = get_object_or_404(CustomUser, username=username)
#         if request.method == 'PATCH':
#             serializer = UsersSerializer(user, data=request.data, partial=True)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         elif request.method == 'DELETE':
#             user.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         serializer = UsersSerializer(user)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     @action(
#         detail=False,
#         methods=['get', 'patch'],
#         url_path='me',
#         url_name='me',
#         permission_classes=(permissions.IsAuthenticated,)
#     )
#     def get_data_for_me(self, request):
#         """Получает информацию о себе с возможностью
#         частичного изменения через patch."""
#         if request.method == 'PATCH':
#             serializer = UsersSerializer(
#                 request.user,
#                 data=request.data,
#                 partial=True,
#             )
#             serializer.is_valid(raise_exception=True)
#             serializer.save(role=request.user.role)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         serializer = UsersSerializer(request.user)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#
# class GetTokenViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
#     """Получение JWT токена с проверкой."""
#     queryset = CustomUser.objects.all()
#     serializer_class = UserGetTokenSerializer
#     permission_classes = (AllowAny,)
#
#     def create(self, request, *args, **kwargs):
#         serializer = UserGetTokenSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         username = serializer.validated_data.get('username')
#         confirmation_code = serializer.validated_data.get('confirmation_code')
#         user = get_object_or_404(CustomUser, username=username)
#         if not default_token_generator.check_token(user, confirmation_code):
#             message = {'confirmation_code': 'Неверный код подтверждения'}
#             return Response(message, status=status.HTTP_400_BAD_REQUEST)
#         message = {'token': str(AccessToken.for_user(user))}
#         return Response(message, status=status.HTTP_200_OK)
