from django.contrib.auth import authenticate
from django.db.models import Prefetch
from django.utils import timezone
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
from medialibrary.utils.base_views import BaseViewSet


class UserVS(mixins.UpdateModelMixin, BaseViewSet):
    queryset = users_m.User.objects.all()
    serializer_class = users_s.UserSerializer
    filterset_class = users_f.UserFilter
    action_permissions = {
        "login": permissions.AllowAny,
        "register": permissions.AllowAny,
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
