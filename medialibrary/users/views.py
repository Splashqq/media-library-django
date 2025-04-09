from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import mixins, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

import medialibrary.users.models as users_m
import medialibrary.users.serializers as users_s
from medialibrary.utils.base_views import BaseViewSet


class UserVS(mixins.UpdateModelMixin, BaseViewSet):
    queryset = users_m.User.objects.all()
    serializer_class = users_s.UserSerializer
    action_permissions = {
        "update": permissions.IsAuthenticated,
        "partial_update": permissions.IsAuthenticated,
    }

    def get_serializer_class(self):
        if self.action == "login":
            return users_s.UserLoginSerializer
        elif self.action == "register":
            return users_s.UserRegisterSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = authenticate(email=email, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        user.last_login = timezone.now()
        user.save()
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        user_serializer = users_s.UserSerializer(user)
        return Response({"token": token.key, "user": user_serializer.data})

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        return Response({"token": token.key})


router = DefaultRouter()
router.register("user", UserVS)

users_urls = router.urls
