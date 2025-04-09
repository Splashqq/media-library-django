from collections import OrderedDict

from rest_framework import serializers


class ReadablePKRF(serializers.PrimaryKeyRelatedField):
    def __init__(self, read_serializer, **kwargs):
        self.read_serializer = read_serializer
        super().__init__(**kwargs)

    def get_queryset(self, *args, **kwargs):
        model = self.read_serializer.Meta.model
        return model.objects.all()

    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            return {}

        if cutoff is not None:
            queryset = queryset[:cutoff]

        return OrderedDict([(item.pk, self.display_value(item)) for item in queryset])

    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        return self.read_serializer(value).data
