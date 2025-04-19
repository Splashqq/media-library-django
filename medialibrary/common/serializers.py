from rest_framework import serializers

import medialibrary.common.models as common_m


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = common_m.Photo
        fields = "__all__"


class VideoSerializer(serializers.ModelSerializer):
    preview = PhotoSerializer(read_only=True)

    class Meta:
        model = common_m.Video
        fields = "__all__"
