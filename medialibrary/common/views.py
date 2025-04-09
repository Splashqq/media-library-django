from rest_framework import permissions
from rest_framework.routers import DefaultRouter

import medialibrary.common.models as common_m
import medialibrary.common.serializers as common_s
from medialibrary.utils.base_views import BaseViewSet


class CountryVS(BaseViewSet):
    queryset = common_m.Country.objects.all()
    serializer_class = common_s.CountrySerializer
    permission_classes = [permissions.AllowAny]


class PhotoVS(BaseViewSet):
    queryset = common_m.Photo.objects.all()
    serializer_class = common_s.PhotoSerializer


router = DefaultRouter()
router.register("country", CountryVS)
router.register("photo", PhotoVS)

common_urls = router.urls
