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


class StaffSerializer(serializers.ModelSerializer):
    person = ReadablePKRF(PersonSerializer)

    class Meta:
        model = catalog_m.Staff
        fields = "__all__"


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = catalog_m.Company
        fields = "__all__"


class MovieSerializer(serializers.ModelSerializer):
    genres = MediaGenreSerializer(many=True, read_only=True)
    company = ReadablePKRF(CompanySerializer)
    poster = ReadablePKRF(common_s.PhotoSerializer)
    movie_staff = StaffSerializer(many=True, read_only=True)
    rating = serializers.FloatField(read_only=True)
    videos = common_s.VideoSerializer(many=True, read_only=True)

    class Meta:
        model = catalog_m.Movie
        exclude = ("staff",)


class MovieRatingSerializer(serializers.ModelSerializer):
    movie = ReadablePKRF(MovieSerializer)

    class Meta:
        model = catalog_m.MovieRating
        fields = "__all__"
        read_only_fields = ("user",)


class SeriesSerializer(serializers.ModelSerializer):
    genres = MediaGenreSerializer(many=True, read_only=True)
    company = ReadablePKRF(CompanySerializer)
    poster = ReadablePKRF(common_s.PhotoSerializer)
    series_staff = StaffSerializer(many=True, read_only=True)
    rating = serializers.FloatField(read_only=True)
    videos = common_s.VideoSerializer(many=True, read_only=True)

    class Meta:
        model = catalog_m.Series
        exclude = ("staff",)


class SeriesRatingSerializer(serializers.ModelSerializer):
    series = ReadablePKRF(SeriesSerializer)

    class Meta:
        model = catalog_m.SeriesRating
        fields = "__all__"
        read_only_fields = ("user",)


class GameSerializer(serializers.ModelSerializer):
    genres = MediaGenreSerializer(many=True, read_only=True)
    company = ReadablePKRF(CompanySerializer)
    poster = ReadablePKRF(common_s.PhotoSerializer)
    rating = serializers.FloatField(read_only=True)
    videos = common_s.VideoSerializer(many=True, read_only=True)

    class Meta:
        model = catalog_m.Game
        fields = "__all__"


class GameRatingSerializer(serializers.ModelSerializer):
    game = ReadablePKRF(GameSerializer)

    class Meta:
        model = catalog_m.GameRating
        fields = "__all__"
        read_only_fields = ("user",)
