from django.contrib import admin

import medialibrary.common.models as common_m


@admin.register(common_m.Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ["id", "type", "created_at"]
    readonly_fields = ["created_at", "updated_at"]
