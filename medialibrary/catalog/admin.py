from django.contrib import admin

import medialibrary.catalog.models as catalog_m


@admin.register(catalog_m.MediaGenre)
class MediaGenreAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(catalog_m.Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ["name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(catalog_m.Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ["person", "movie", "series", "role"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(catalog_m.Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = [
        "title",
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(catalog_m.MovieRating)
class MovieRatingAdmin(admin.ModelAdmin):
    list_display = ["movie", "user", "rating"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(catalog_m.Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(catalog_m.Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = [
        "title",
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(catalog_m.SeriesRating)
class SeriesRatingAdmin(admin.ModelAdmin):
    list_display = ["series", "user", "rating"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(catalog_m.Game)
class GameAdmin(admin.ModelAdmin):
    list_display = [
        "title",
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(catalog_m.GameRating)
class GameRatingAdmin(admin.ModelAdmin):
    list_display = ["game", "user", "rating"]
    readonly_fields = ["created_at", "updated_at"]
