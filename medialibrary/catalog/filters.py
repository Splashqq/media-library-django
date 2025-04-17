from django_filters import rest_framework as filters

import medialibrary.catalog.models as catalog_m


class PersonFilter(filters.FilterSet):
    class Meta:
        model = catalog_m.Person
        fields = {
            "name": ["icontains"],
        }


class MediaContentFilter(filters.FilterSet):
    release_date = filters.NumberFilter(
        field_name="release_date",
        lookup_expr="year",
    )
    release_date__gte = filters.NumberFilter(
        field_name="release_date",
        lookup_expr="year__gte",
    )
    release_date__lte = filters.NumberFilter(
        field_name="release_date",
        lookup_expr="year__lte",
    )
    genres = filters.ModelMultipleChoiceFilter(
        field_name="genres",
        queryset=catalog_m.MediaGenre.objects.all(),
        label="Genres",
        conjoined=True,
    )

    class Meta:
        fields = {
            "title": ["icontains"],
        }


class MovieFilter(MediaContentFilter):
    class Meta(MediaContentFilter.Meta):
        model = catalog_m.Movie


class SeriesFilter(MediaContentFilter):
    class Meta(MediaContentFilter.Meta):
        model = catalog_m.Series


class GameFilter(MediaContentFilter):
    class Meta(MediaContentFilter.Meta):
        model = catalog_m.Game
