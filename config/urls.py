from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from medialibrary.catalog.views import catalog_urls
from medialibrary.common.views import common_urls
from medialibrary.users.views import users_urls

api_urls = [
    path("users/", include(users_urls)),
    path("common/", include(common_urls)),
    path("catalog/", include(catalog_urls)),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
]
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urls)),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            re_path(r"^__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
