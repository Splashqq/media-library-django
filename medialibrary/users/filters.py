from django_filters import rest_framework as filters

import medialibrary.users.models as users_m


class UserFilter(filters.FilterSet):
    class Meta:
        model = users_m.User
        fields = {
            "username": ["icontains"],
        }
