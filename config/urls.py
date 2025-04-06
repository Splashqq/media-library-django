from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from medialibrary.users.views import users_urls

api_urls = [
    path("users/", include(users_urls)),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
]
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urls)),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            re_path(r"^__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
