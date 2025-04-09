from rest_framework.routers import DefaultRouter

import medialibrary.catalog.models as catalog_m
import medialibrary.catalog.serializers as catalog_s
from medialibrary.utils.base_views import BaseViewSet


class MediaGenreVS(BaseViewSet):
    queryset = catalog_m.MediaGenre.objects.all()
    serializer_class = catalog_s.MediaGenreSerializer


class PersonVS(BaseViewSet):
    queryset = catalog_m.Person.objects.all()
    serializer_class = catalog_s.PersonSerializer


class MovieVS(BaseViewSet):
    queryset = catalog_m.Movie.objects.all()
    serializer_class = catalog_s.MovieSerializer

    def get_queryset(self):
        qs = self.queryset
        qs = self.filter_queryset(qs)
        return qs.select_related("poster", "country").prefetch_related(
            "directors", "actors", "genres"
        )


class SeriesVS(BaseViewSet):
    queryset = catalog_m.Series.objects.all()
    serializer_class = catalog_s.SeriesSerializer

    def get_queryset(self):
        qs = self.queryset
        qs = self.filter_queryset(qs)
        return qs.select_related("poster", "country").prefetch_related(
            "directors", "actors", "genres"
        )


class DeveloperVS(BaseViewSet):
    queryset = catalog_m.Developer.objects.all()
    serializer_class = catalog_s.DeveloperSerializer


class GameVS(BaseViewSet):
    queryset = catalog_m.Game.objects.all()
    serializer_class = catalog_s.GameSerializer

    def get_queryset(self):
        qs = self.queryset
        qs = self.filter_queryset(qs)
        return qs.select_related("poster", "developer").prefetch_related("genres")


class AnimeVS(BaseViewSet):
    queryset = catalog_m.Anime.objects.all()
    serializer_class = catalog_s.AnimeSerializer

    def get_queryset(self):
        qs = self.queryset
        qs = self.filter_queryset(qs)
        return qs.select_related("poster").prefetch_related("genres", "directors")


router = DefaultRouter()
router.register("media_genre", MediaGenreVS)
router.register("person", PersonVS)
router.register("developer", DeveloperVS)
router.register("movie", MovieVS)
router.register("series", SeriesVS)
router.register("game", GameVS)
router.register("anime", AnimeVS)

catalog_urls = router.urls
