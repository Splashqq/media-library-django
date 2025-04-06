from django.contrib import admin

import medialibrary.users.models as users_m


@admin.register(users_m.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "username", "created_at"]
