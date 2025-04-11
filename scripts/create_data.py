import os
import random
import sys
from datetime import timedelta
from random import choice, sample

import django

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

import medialibrary.catalog.constants as catalog_c
import medialibrary.catalog.models as catalog_m
import medialibrary.common.models as common_m


def create_persons():
    persons = []
    for i in range(1, 10):
        p, _ = catalog_m.Person.objects.get_or_create(
            name=f"name{i}",
        )
        persons.append(p)
    return persons


def create_genres():
    genres = []
    for i in range(1, 7):
        g, _ = catalog_m.MediaGenre.objects.get_or_create(name=f"genre{i}")
        genres.append(g)
    return genres


def create_companies():
    companies = []
    for i in range(1, 5):
        c, _ = catalog_m.Company.objects.get_or_create(name=f"company{i}")
        companies.append(c)
    return companies


def create_movies(companies, genres):
    movies = []
    for i in range(1, 10):
        m, _ = catalog_m.Movie.objects.get_or_create(
            title=f"movie{i}",
            description=f"movie{i}",
            release_date="2024-08-04",
            duration=timedelta(hours=2),
            company=choice(companies),
        )
        m.genres.set(sample(genres, 3))
        movies.append(m)
    return movies


def create_series(companies, genres):
    series = []
    for i in range(1, 10):
        s, _ = catalog_m.Series.objects.get_or_create(
            title=f"series{i}",
            description=f"series{i}",
            release_date="2024-08-04",
            type=choice(catalog_c.SERIES_TYPES)[0],
            episode_duration=timedelta(minutes=20),
            episodes=15,
            company=choice(companies),
        )
        s.genres.set(sample(genres, 3))
        series.append(s)
    return series


def create_games(companies, genres):
    for i in range(1, 10):
        g, _ = catalog_m.Game.objects.get_or_create(
            title=f"game{i}",
            description=f"game{i}",
            release_date="2024-08-04",
            company=choice(companies),
        )
        g.genres.set(sample(genres, 3))


def create_staffs(persons, movies, series):
    for person in persons:
        catalog_m.Staff.objects.create(
            person=person,
            movie=choice(movies),
            role=choice(catalog_c.STAFF_ROLES)[0],
        )
        catalog_m.Staff.objects.create(
            person=person,
            series=choice(series),
            role=choice(catalog_c.STAFF_ROLES)[0],
        )


if __name__ == "__main__":
    print("Creating data...")
    persons = create_persons()
    genres = create_genres()
    companies = create_companies()
    movies = create_movies(companies, genres)
    series = create_series(companies, genres)
    create_games(companies, genres)
    create_staffs(persons, movies, series)
    print("Done!")
