import inspect

from rest_framework import mixins, permissions, viewsets
from rest_framework.pagination import PageNumberPagination


class DynamicResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 200


class ActionBasedPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        custom_permission = getattr(view, "action_permissions", {}).get(view.action)
        if not custom_permission:
            return super().has_permission(request, view)

        if inspect.isclass(custom_permission):
            return custom_permission().has_permission(request, view)

        return custom_permission(request)


class BaseViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    permission_classes = [ActionBasedPermission]
    pagination_class = DynamicResultsSetPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
