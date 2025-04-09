from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

import medialibrary.catalog.constants as catalog_c
from medialibrary.utils.models import TimeStampedModel


class Person(TimeStampedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    born = models.DateField(blank=True, null=True)
    died = models.DateField(blank=True, null=True)
    type = models.IntegerField(choices=catalog_c.PERSON_TYPES)

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "Persons"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


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
    genres = models.ManyToManyField("catalog.MediaGenre", related_name="movie_genres")
    country = models.ForeignKey(
        "common.Country",
        on_delete=models.SET_NULL,
        related_name="movie_country",
        null=True,
        blank=True,
    )
    directors = models.ManyToManyField("catalog.Person", related_name="movie_directors")
    actors = models.ManyToManyField("catalog.Person", related_name="movie_actors")
    avg_rating = models.IntegerField(
        validators=[
            MinValueValidator(Decimal("1")),
            MaxValueValidator(10),
        ],
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Movie"
        verbose_name_plural = "Movies"

    def __str__(self):
        return self.title


class Series(TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField(blank=True, null=True)
    episodes = models.PositiveIntegerField()
    poster = models.ForeignKey(
        "common.Photo",
        on_delete=models.SET_NULL,
        related_name="series_poster",
        null=True,
        blank=True,
    )
    genres = models.ManyToManyField("catalog.MediaGenre", related_name="series_genres")
    country = models.ForeignKey(
        "common.Country",
        on_delete=models.SET_NULL,
        related_name="series_country",
        null=True,
        blank=True,
    )
    directors = models.ManyToManyField(
        "catalog.Person", related_name="series_directors"
    )
    actors = models.ManyToManyField("catalog.Person", related_name="series_actors")
    avg_rating = models.IntegerField(
        validators=[
            MinValueValidator(Decimal("1")),
            MaxValueValidator(10),
        ],
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Series"
        verbose_name_plural = "Series"

    def __str__(self):
        return self.title


class Developer(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Developer"
        verbose_name_plural = "Developers"

    def __str__(self):
        return self.name


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
    genres = models.ManyToManyField("catalog.MediaGenre", related_name="game_genres")
    developer = models.ForeignKey(
        "catalog.Developer",
        on_delete=models.SET_NULL,
        related_name="game_developer",
        null=True,
        blank=True,
    )
    avg_rating = models.IntegerField(
        validators=[
            MinValueValidator(Decimal("1")),
            MaxValueValidator(10),
        ],
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Game"
        verbose_name_plural = "Games"

    def __str__(self):
        return self.title


class Anime(TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField(null=True, blank=True)
    poster = models.ForeignKey(
        "common.Photo",
        on_delete=models.SET_NULL,
        related_name="anime_poster",
        null=True,
        blank=True,
    )
    genres = models.ManyToManyField("catalog.MediaGenre", related_name="anime_genres")
    directors = models.ManyToManyField("catalog.Person", related_name="anime_directors")
    episodes = models.PositiveIntegerField()
    avg_rating = models.IntegerField(
        validators=[
            MinValueValidator(Decimal("1")),
            MaxValueValidator(10),
        ],
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Anime"
        verbose_name_plural = "Animes"

    def __str__(self):
        return self.title
