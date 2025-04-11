from rest_framework import permissions
from rest_framework.routers import DefaultRouter

import medialibrary.common.models as common_m
import medialibrary.common.serializers as common_s
from medialibrary.utils.base_views import BaseViewSet


class PhotoVS(BaseViewSet):
    queryset = common_m.Photo.objects.all()
    serializer_class = common_s.PhotoSerializer

    action_permissions = {
        "list": permissions.AllowAny,
        "retrieve": permissions.AllowAny,
    }


router = DefaultRouter()
router.register("photo", PhotoVS)

common_urls = router.urls
