import uuid

from django.db import models

import medialibrary.common.constants as common_c
from medialibrary.utils.models import TimeStampedModel


def photo_upload_to(instance, filename, *args, **kwargs) -> str:
    ext = filename.split(".")[-1]
    path = instance.get_type_display()
    new_filename = str(uuid.uuid4())
    return f"photos/{path}/{new_filename}.{ext}"


class Photo(TimeStampedModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="photos", null=True
    )
    type = models.IntegerField("Type", choices=common_c.PHOTO_TYPES)
    photo = models.ImageField("Image", upload_to=photo_upload_to)
    movie = models.ForeignKey(
        "catalog.Movie",
        on_delete=models.SET_NULL,
        related_name="photos",
        blank=True,
        null=True,
    )
    game = models.ForeignKey(
        "catalog.Game",
        on_delete=models.SET_NULL,
        related_name="photos",
        blank=True,
        null=True,
    )
    series = models.ForeignKey(
        "catalog.Series",
        on_delete=models.SET_NULL,
        related_name="photos",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Photo"
        verbose_name_plural = "Photos"

    def __str__(self):
        return f"Photo {self.pk}"
