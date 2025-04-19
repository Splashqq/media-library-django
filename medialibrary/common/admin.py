from django.contrib import admin

import medialibrary.common.models as common_m


@admin.register(common_m.Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ["id", "type", "created_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(common_m.Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ["id", "type", "movie", "series", "game", "created_at"]
    readonly_fields = ["created_at", "updated_at"]
