from django.contrib import admin

import medialibrary.users.models as users_m


@admin.register(users_m.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "username", "created_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(users_m.UserMovieCollection)
class UserMovieCollectionAdmin(admin.ModelAdmin):
    list_display = ["user", "movie", "status"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(users_m.UserSeriesCollection)
class UserSeriesCollectionAdmin(admin.ModelAdmin):
    list_display = ["user", "series", "status"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(users_m.UserGameCollection)
class UserGameCollectionAdmin(admin.ModelAdmin):
    list_display = ["user", "game", "status"]
    readonly_fields = ["created_at", "updated_at"]
