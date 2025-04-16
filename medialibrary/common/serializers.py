from rest_framework import serializers

import medialibrary.common.models as common_m


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = common_m.Photo
        fields = "__all__"
