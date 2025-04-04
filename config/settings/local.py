from .base import *

TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG

if not TESTING:
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
    INSTALLED_APPS += ["debug_toolbar"]

INTERNAL_IPS = ["127.0.0.1"]

DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": [
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ],
    "SHOW_TEMPLATE_CONTEXT": True,
    "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
}

if AWS_STORAGE_BUCKET_NAME == "":
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    FILE_UPLOAD_PERMISSIONS = 0o644
