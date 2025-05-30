import uuid

from django.contrib.auth import authenticate
from django.core.cache import cache
from django.db.models import Prefetch
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import mixins, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

import medialibrary.catalog.models as catalog_m
import medialibrary.common.models as common_m
import medialibrary.users.filters as users_f
import medialibrary.users.models as users_m
import medialibrary.users.serializers as users_s
from medialibrary.users.docs import (
    change_password_extend_schema,
    login_extend_schema,
    register_extend_schema,
    reset_password_confirm_extend_schema,
    reset_password_extend_schema,
)
from medialibrary.users.mailer import Mailer
from medialibrary.utils.base_views import BaseViewSet

MAILER = Mailer()


class UserVS(mixins.UpdateModelMixin, BaseViewSet):
    queryset = users_m.User.objects.all()
    serializer_class = users_s.UserSerializer
    filterset_class = users_f.UserFilter
    action_permissions = {
        "login": permissions.AllowAny,
        "register": permissions.AllowAny,
        "reset_password": permissions.AllowAny,
        "reset_password_confirm": permissions.AllowAny,
    }

    def get_serializer_class(self):
        if self.action == "login":
            return users_s.UserLoginSerializer
        elif self.action == "register":
            return users_s.UserRegisterSerializer
        elif self.action == "change_password":
            return users_s.UserChangePasswordSerializer
        elif self.action == "reset_password":
            return users_s.UserRequestPasswordResetSerializer
        return super().get_serializer_class()

    @login_extend_schema
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

    @register_extend_schema
    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.create(user=user)
        return Response({"token": token.key})

    @change_password_extend_schema
    @action(detail=False, methods=["post"])
    def change_password(self, request):
        serializer = self.get_serializer_class()(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response(
            {"detail": "Password changed successfully"}, status=status.HTTP_200_OK
        )

    @reset_password_extend_schema
    @method_decorator(ratelimit(key="ip", rate="1/10m", method="POST"))
    @action(detail=False, methods=["post"])
    def reset_password(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = users_m.User.objects.get(email=email)

        token = uuid.uuid4()
        temp_password = get_random_string(10)

        cache_data = {
            "user_id": user.id,
            "temp_password": temp_password,
            "email": email,
        }
        cache.set(f"password_reset_{token}", cache_data, timeout=60 * 10)  # 10 min

        reset_url = UserVS.reverse_action(
            self, url_name="password-reset-confirm", kwargs={"token": str(token)}
        )

        MAILER.send_password_reset_message(user.email, reset_url, email, temp_password)
        return Response({"detail": "Message sent"})

    @reset_password_confirm_extend_schema
    @action(
        detail=False,
        methods=["get"],
        url_path="password-reset-confirm/(?P<token>[0-9a-fA-F-]+)",
        url_name="password-reset-confirm",
    )
    def reset_password_confirm(self, request, token=None):
        if not token:
            return Response(
                {"error": "Token is required"}, status=status.HTTP_404_NOT_FOUND
            )

        cache_key = f"password_reset_{token}"
        cache_data = cache.get(cache_key)

        if cache_data is None:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = users_m.User.objects.get(id=cache_data["user_id"])
        except users_m.User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        user.set_password(cache_data["temp_password"])
        user.save()

        cache.delete(cache_key)
        return Response({"detail": "Password was changed"}, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        if serializer.instance != self.request.user:
            raise APIException("Can't edit profile")
        serializer.save(user=self.request.user)


class UserMovieCollectionVS(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    BaseViewSet,
):
    queryset = users_m.UserMovieCollection.objects.all()
    serializer_class = users_s.UserMovieCollectionSerializer

    action_permissions = {
        "list": permissions.AllowAny,
        "retrieve": permissions.AllowAny,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related(
            Prefetch(
                "movie",
                queryset=catalog_m.Movie.objects.all()
                .select_related("poster", "company")
                .prefetch_related(
                    "photos",
                    "genres",
                    Prefetch(
                        "videos",
                        queryset=common_m.Video.objects.all().select_related("preview"),
                    ),
                    Prefetch(
                        "movie_staff",
                        queryset=catalog_m.Staff.objects.all().select_related("person"),
                    ),
                ),
            ),
        )

    def perform_create(self, serializer):
        if users_m.UserMovieCollection.objects.filter(
            user=self.request.user, movie=serializer.validated_data["movie"]
        ).exists():
            raise APIException("Movie already exists in collection")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise APIException("Can't edit collection")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise APIException("Can't delete collection")
        instance.delete()


class UserSeriesCollectionVS(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    BaseViewSet,
):
    queryset = users_m.UserSeriesCollection.objects.all()
    serializer_class = users_s.UserSeriesCollectionSerializer

    action_permissions = {
        "list": permissions.AllowAny,
        "retrieve": permissions.AllowAny,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related(
            Prefetch(
                "series",
                queryset=catalog_m.Series.objects.all()
                .select_related("poster", "company")
                .prefetch_related(
                    "photos",
                    "genres",
                    Prefetch(
                        "videos",
                        queryset=common_m.Video.objects.all().select_related("preview"),
                    ),
                    Prefetch(
                        "series_staff",
                        queryset=catalog_m.Staff.objects.all().select_related("person"),
                    ),
                ),
            ),
        )

    def perform_create(self, serializer):
        if users_m.UserSeriesCollection.objects.filter(
            user=self.request.user, series=serializer.validated_data["series"]
        ).exists():
            raise APIException("Series already exists in collection")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise APIException("Can't edit collection")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise APIException("Can't delete collection")
        instance.delete()


class UserGameCollectionVS(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    BaseViewSet,
):
    queryset = users_m.UserGameCollection.objects.all()
    serializer_class = users_s.UserGameCollectionSerializer

    action_permissions = {
        "list": permissions.AllowAny,
        "retrieve": permissions.AllowAny,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related(
            Prefetch(
                "game",
                queryset=catalog_m.Game.objects.all()
                .select_related("poster", "company")
                .prefetch_related(
                    "photos",
                    "genres",
                    Prefetch(
                        "videos",
                        queryset=common_m.Video.objects.all().select_related("preview"),
                    ),
                ),
            ),
        )

    def perform_create(self, serializer):
        if users_m.UserGameCollection.objects.filter(
            user=self.request.user, game=serializer.validated_data["game"]
        ).exists():
            raise APIException("Game already exists in collection")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise APIException("Can't edit collection")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise APIException("Can't delete collection")
        instance.delete()


router = DefaultRouter()
router.register("user", UserVS)
router.register("movie_collection", UserMovieCollectionVS)
router.register("series_collection", UserSeriesCollectionVS)
router.register("game_collection", UserGameCollectionVS)

users_urls = router.urls
