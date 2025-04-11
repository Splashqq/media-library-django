from rest_framework import permissions
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
        return qs.select_related("poster").prefetch_related("genres")


class SeriesVS(BaseViewSet):
    queryset = catalog_m.Series.objects.all()
    serializer_class = catalog_s.SeriesSerializer

    action_permissions = {
        "list": permissions.AllowAny,
        "retrieve": permissions.AllowAny,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related("poster").prefetch_related("genres")


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
        return qs.select_related("poster").prefetch_related("genres")


router = DefaultRouter()
router.register("media_genre", MediaGenreVS)
router.register("person", PersonVS)
router.register("company", CompanyVS)
router.register("movie", MovieVS)
router.register("series", SeriesVS)
router.register("game", GameVS)

catalog_urls = router.urls
