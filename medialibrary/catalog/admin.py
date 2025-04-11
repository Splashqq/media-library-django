from django.contrib import admin

import medialibrary.catalog.models as catalog_m


@admin.register(catalog_m.MediaGenre)
class MediaGenreAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(catalog_m.Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(catalog_m.Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ["person", "movie", "series", "role"]


@admin.register(catalog_m.Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = [
        "title",
    ]


@admin.register(catalog_m.Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]


@admin.register(catalog_m.Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = [
        "title",
    ]


@admin.register(catalog_m.Game)
class GameAdmin(admin.ModelAdmin):
    list_display = [
        "title",
    ]
