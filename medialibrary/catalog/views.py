from django.db.models import Avg, Prefetch
from rest_framework import mixins, permissions
from rest_framework.exceptions import APIException
from rest_framework.routers import DefaultRouter

import medialibrary.catalog.models as catalog_m
import medialibrary.catalog.serializers as catalog_s
from medialibrary.utils.base_views import BaseViewSet


class MediaGenreVS(BaseViewSet):
    queryset = catalog_m.MediaGenre.objects.all()
    serializer_class = catalog_s.MediaGenreSerializer

    action_permissions = {
        "list": permissions.AllowAny,
        "retrieve": permissions.AllowAny,
    }


class PersonVS(BaseViewSet):
    queryset = catalog_m.Person.objects.all()
    serializer_class = catalog_s.PersonSerializer

    action_permissions = {
        "list": permissions.AllowAny,
        "retrieve": permissions.AllowAny,
    }


class MovieVS(BaseViewSet):
    queryset = catalog_m.Movie.objects.all()
    serializer_class = catalog_s.MovieSerializer

    action_permissions = {
        "list": permissions.AllowAny,
        "retrieve": permissions.AllowAny,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return (
            qs.annotate(rating=Avg("movie__rating"))
            .select_related("poster", "company")
            .prefetch_related(
                "staff",
                "genres",
                Prefetch(
                    "movie_staff",
                    queryset=catalog_m.Staff.objects.all().select_related("person"),
                ),
            )
        )


class MovieRatingVS(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    BaseViewSet,
):
    queryset = catalog_m.MovieRating.objects.all()
    serializer_class = catalog_s.MovieRatingSerializer

    action_permissions = {
        "list": permissions.AllowAny,
        "retrieve": permissions.AllowAny,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related(
            "user",
            Prefetch(
                "movie",
                queryset=catalog_m.Movie.objects.all()
                .select_related("poster", "company")
                .prefetch_related(
                    "staff",
                    "genres",
                    Prefetch(
                        "movie_staff",
                        queryset=catalog_m.Staff.objects.all().select_related("person"),
                    ),
                ),
            ),
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise APIException("Can't edit rating")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise APIException("Can't delete rating")
        instance.delete()


class SeriesVS(BaseViewSet):
    queryset = catalog_m.Series.objects.all()
    serializer_class = catalog_s.SeriesSerializer

    action_permissions = {
        "list": permissions.AllowAny,
        "retrieve": permissions.AllowAny,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return (
            qs.annotate(rating=Avg("series__rating"))
            .select_related("poster", "company")
            .prefetch_related(
                "staff",
                "genres",
                Prefetch(
                    "series_staff",
                    queryset=catalog_m.Staff.objects.all().select_related("person"),
                ),
            )
        )


class SeriesRatingVS(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    BaseViewSet,
):
    queryset = catalog_m.SeriesRating.objects.all()
    serializer_class = catalog_s.SeriesRatingSerializer

    action_permissions = {
        "list": permissions.AllowAny,
        "retrieve": permissions.AllowAny,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related(
            "user",
            Prefetch(
                "series",
                queryset=catalog_m.Series.objects.all()
                .select_related("poster", "company")
                .prefetch_related(
                    "staff",
                    "genres",
                    Prefetch(
                        "series_staff",
                        queryset=catalog_m.Staff.objects.all().select_related("person"),
                    ),
                ),
            ),
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise APIException("Can't edit rating")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise APIException("Can't delete rating")
        instance.delete()


class CompanyVS(BaseViewSet):
    queryset = catalog_m.Company.objects.all()
    serializer_class = catalog_s.CompanySerializer

    action_permissions = {
        "list": permissions.AllowAny,
        "retrieve": permissions.AllowAny,
    }


class GameVS(BaseViewSet):
    queryset = catalog_m.Game.objects.all()
    serializer_class = catalog_s.GameSerializer

    action_permissions = {
        "list": permissions.AllowAny,
        "retrieve": permissions.AllowAny,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return (
            qs.annotate(rating=Avg("game__rating"))
            .select_related("poster", "company")
            .prefetch_related("genres")
        )


class GameRatingVS(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    BaseViewSet,
):
    queryset = catalog_m.GameRating.objects.all()
    serializer_class = catalog_s.GameRatingSerializer

    action_permissions = {
        "list": permissions.AllowAny,
        "retrieve": permissions.AllowAny,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related(
            "user",
            Prefetch(
                "game",
                queryset=catalog_m.Game.objects.all()
                .select_related("poster", "company")
                .prefetch_related("genres"),
            ),
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise APIException("Can't edit rating")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise APIException("Can't delete rating")
        instance.delete()


router = DefaultRouter()
router.register("media_genre", MediaGenreVS)
router.register("person", PersonVS)
router.register("company", CompanyVS)
router.register("movie", MovieVS)
router.register("movie_rating", MovieRatingVS)
router.register("series", SeriesVS)
router.register("series_rating", SeriesRatingVS)
router.register("game", GameVS)
router.register("game_rating", GameRatingVS)

catalog_urls = router.urls
