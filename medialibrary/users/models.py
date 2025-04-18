import uuid

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

import medialibrary.users.constants as users_c
from medialibrary.utils.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=45, unique=True)
    is_staff = models.BooleanField(default=False)
    avatar = models.ForeignKey(
        "common.Photo", on_delete=models.SET_NULL, null=True, related_name="users"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email


class UserMovieCollection(TimeStampedModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    movie = models.ForeignKey("catalog.Movie", on_delete=models.CASCADE)
    status = models.IntegerField(choices=users_c.USER_MEDIA_COLLECTION_STATUSES)

    class Meta:
        verbose_name = "Movie Collection"
        verbose_name_plural = "Movie Collections"
        unique_together = ("user", "movie")

    def __str__(self):
        return self.movie.title


class UserSeriesCollection(TimeStampedModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    series = models.ForeignKey("catalog.Series", on_delete=models.CASCADE)
    status = models.IntegerField(choices=users_c.USER_MEDIA_COLLECTION_STATUSES)

    class Meta:
        verbose_name = "Series Collection"
        verbose_name_plural = "Series Collections"
        unique_together = ("user", "series")

    def __str__(self):
        return self.series.title


class UserGameCollection(TimeStampedModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    game = models.ForeignKey("catalog.Game", on_delete=models.CASCADE)
    status = models.IntegerField(choices=users_c.USER_GAME_COLLECTION_STATUSES)

    class Meta:
        verbose_name = "Game Collection"
        verbose_name_plural = "Game Collections"
        unique_together = ("user", "game")

    def __str__(self):
        return self.game.title
