import uuid

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.validators import FileExtensionValidator
from django.db import models
from moviepy.editor import VideoFileClip

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


def video_upload_to(instance, filename, *args, **kwargs) -> str:
    ext = filename.split(".")[-1]
    path = instance.get_type_display()
    new_filename = str(uuid.uuid4())
    return f"videos/{path}/{new_filename}.{ext}"


class Video(TimeStampedModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="videos",
        null=True,
        blank=True,
    )
    type = models.IntegerField("Type", choices=common_c.VIDEO_TYPES)
    preview = models.ForeignKey(
        "common.Photo", on_delete=models.SET_NULL, null=True, blank=True
    )
    video = models.FileField(
        "Video",
        upload_to=video_upload_to,
        validators=[FileExtensionValidator(["mov", "avi", "mp4", "webm", "mkv"])],
    )
    movie = models.ForeignKey(
        "catalog.Movie",
        on_delete=models.SET_NULL,
        related_name="videos",
        blank=True,
        null=True,
    )
    game = models.ForeignKey(
        "catalog.Game",
        on_delete=models.SET_NULL,
        related_name="videos",
        blank=True,
        null=True,
    )
    series = models.ForeignKey(
        "catalog.Series",
        on_delete=models.SET_NULL,
        related_name="videos",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videos"
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(
                        movie__isnull=False, series__isnull=True, game__isnull=True
                    )
                    | models.Q(
                        movie__isnull=True, series__isnull=False, game__isnull=True
                    )
                    | models.Q(
                        movie__isnull=True, series__isnull=True, game__isnull=False
                    )
                ),
                name="exactly_one_of_movie_series_game_video",
            ),
        ]

    def __str__(self):
        return f"Video {self.pk}"

    def set_preview(self):
        tempvideo = NamedTemporaryFile()
        tempvideo.write(self.video.file.read())
        tempvideo.flush()
        tempvideo.seek(0)

        clip = VideoFileClip(tempvideo.name)
        temppreview = NamedTemporaryFile(suffix=".jpg")
        clip.save_frame(temppreview.name, t=min(1, clip.duration))
        temppreview.flush()
        temppreview.seek(0)

        self.preview = Photo.objects.create(
            type=common_c.PHOTO_TYPE_VIDEO_PREVIEW, photo=File(temppreview)
        )

    def save(self, *args, **kwargs):
        self.set_preview()
        super().save(*args, **kwargs)
