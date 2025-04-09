from rest_framework import serializers

import medialibrary.catalog.models as catalog_m
import medialibrary.common.serializers as common_s
from medialibrary.utils.drf import ReadablePKRF


class MediaGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = catalog_m.MediaGenre
        fields = "__all__"


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = catalog_m.Person
        fields = "__all__"


class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = catalog_m.Developer
        fields = "__all__"


class MovieSerializer(serializers.ModelSerializer):
    genres = MediaGenreSerializer(many=True, read_only=True)
    directors = PersonSerializer(many=True, read_only=True)
    actors = PersonSerializer(many=True, read_only=True)
    country = ReadablePKRF(common_s.CountrySerializer)
    poster = ReadablePKRF(common_s.PhotoSerializer)

    class Meta:
        model = catalog_m.Movie
        fields = "__all__"


class SeriesSerializer(serializers.ModelSerializer):
    genres = MediaGenreSerializer(many=True, read_only=True)
    directors = PersonSerializer(many=True, read_only=True)
    actors = PersonSerializer(many=True, read_only=True)
    country = ReadablePKRF(common_s.CountrySerializer)
    poster = ReadablePKRF(common_s.PhotoSerializer)

    class Meta:
        model = catalog_m.Series
        fields = "__all__"


class GameSerializer(serializers.ModelSerializer):
    genres = MediaGenreSerializer(many=True, read_only=True)
    developer = ReadablePKRF(DeveloperSerializer)
    poster = ReadablePKRF(common_s.PhotoSerializer)

    class Meta:
        model = catalog_m.Game
        fields = "__all__"


class AnimeSerializer(serializers.ModelSerializer):
    genres = MediaGenreSerializer(many=True, read_only=True)
    directors = PersonSerializer(many=True, read_only=True)
    poster = ReadablePKRF(common_s.PhotoSerializer)

    class Meta:
        model = catalog_m.Anime
        fields = "__all__"
