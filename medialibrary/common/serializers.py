from rest_framework import serializers

import medialibrary.common.models as common_m


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = common_m.Country
        fields = "__all__"


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = common_m.Photo
        fields = "__all__"
