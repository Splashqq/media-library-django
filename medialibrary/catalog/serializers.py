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
    staff = StaffSerializer(many=True, read_only=True)

    class Meta:
        model = catalog_m.Movie
        fields = "__all__"


class SeriesSerializer(serializers.ModelSerializer):
    genres = MediaGenreSerializer(many=True, read_only=True)
    company = ReadablePKRF(CompanySerializer)
    poster = ReadablePKRF(common_s.PhotoSerializer)

    class Meta:
        model = catalog_m.Series
        fields = "__all__"


class GameSerializer(serializers.ModelSerializer):
    genres = MediaGenreSerializer(many=True, read_only=True)
    company = ReadablePKRF(CompanySerializer)
    poster = ReadablePKRF(common_s.PhotoSerializer)

    class Meta:
        model = catalog_m.Game
        fields = "__all__"
