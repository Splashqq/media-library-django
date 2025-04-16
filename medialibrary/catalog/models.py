from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

import medialibrary.catalog.constants as catalog_c
from medialibrary.utils.models import TimeStampedModel


class Person(TimeStampedModel):
    name = models.TextField()

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "Persons"

    def __str__(self):
        return f"{self.name}"


class Staff(TimeStampedModel):
    person = models.ForeignKey(
        "catalog.Person",
        on_delete=models.CASCADE,
        related_name="staff_person",
    )
    movie = models.ForeignKey(
        "catalog.Movie",
        on_delete=models.SET_NULL,
        related_name="movie_staff",
        null=True,
        blank=True,
    )
    series = models.ForeignKey(
        "catalog.Series",
        on_delete=models.SET_NULL,
        related_name="series_staff",
        null=True,
        blank=True,
    )
    role = models.IntegerField(choices=catalog_c.STAFF_ROLES)

    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staff"
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(movie__isnull=False, series__isnull=True)
                    | models.Q(movie__isnull=True, series__isnull=False)
                ),
                name="exactly_one_of_movie_series_game",
            )
        ]

    def __str__(self):
        return f"{self.person}"


class Company(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class MediaGenre(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Media Genre"
        verbose_name_plural = "Media Genres"

    def __str__(self):
        return self.name


class Movie(TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    poster = models.ForeignKey(
        "common.Photo",
        on_delete=models.SET_NULL,
        related_name="movie_poster",
        null=True,
        blank=True,
    )
    genres = models.ManyToManyField("catalog.MediaGenre", related_name="movies")
    company = models.ForeignKey(
        "catalog.Company", on_delete=models.SET_NULL, null=True, blank=True
    )
    staff = models.ManyToManyField(
        "catalog.Person", through="catalog.Staff", related_name="movies"
    )

    class Meta:
        verbose_name = "Movie"
        verbose_name_plural = "Movies"

    def __str__(self):
        return self.title


class MovieRating(TimeStampedModel):
    movie = models.ForeignKey(
        "catalog.Movie", on_delete=models.CASCADE, related_name="ratings"
    )
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ],
    )

    class Meta:
        verbose_name = "Movie Rating"
        verbose_name_plural = "Movie Ratings"
        unique_together = ("movie", "user")

    def __str__(self):
        return self.movie.title


class Series(TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField(blank=True, null=True)
    type = models.IntegerField(choices=catalog_c.SERIES_TYPES, null=True, blank=True)
    episode_duration = models.DurationField(blank=True, null=True)
    episodes = models.PositiveIntegerField(blank=True, null=True)
    poster = models.ForeignKey(
        "common.Photo",
        on_delete=models.SET_NULL,
        related_name="series_poster",
        null=True,
        blank=True,
    )
    genres = models.ManyToManyField("catalog.MediaGenre", related_name="series")
    company = models.ForeignKey(
        "catalog.Company", on_delete=models.SET_NULL, null=True, blank=True
    )
    staff = models.ManyToManyField(
        "catalog.Person", through="catalog.Staff", related_name="series"
    )

    class Meta:
        verbose_name = "Series"
        verbose_name_plural = "Series"

    def __str__(self):
        return self.title


class SeriesRating(TimeStampedModel):
    series = models.ForeignKey(
        "catalog.Series", on_delete=models.CASCADE, related_name="ratings"
    )
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ],
    )

    class Meta:
        verbose_name = "Series Rating"
        verbose_name_plural = "Series Ratings"
        unique_together = ("series", "user")

    def __str__(self):
        return self.series.title


class Game(TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField(null=True, blank=True)
    poster = models.ForeignKey(
        "common.Photo",
        on_delete=models.SET_NULL,
        related_name="game_poster",
        null=True,
        blank=True,
    )
    genres = models.ManyToManyField("catalog.MediaGenre", related_name="games")
    company = models.ForeignKey(
        "catalog.Company", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = "Game"
        verbose_name_plural = "Games"

    def __str__(self):
        return self.title


class GameRating(TimeStampedModel):
    game = models.ForeignKey(
        "catalog.Game", on_delete=models.CASCADE, related_name="ratings"
    )
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ],
    )

    class Meta:
        verbose_name = "Game Rating"
        verbose_name_plural = "Game Ratings"
        unique_together = ("game", "user")

    def __str__(self):
        return self.game.title
