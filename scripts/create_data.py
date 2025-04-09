import os
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


def create_countries():
    countries = []
    for i in range(1, 10):
        c, _ = common_m.Country.objects.get_or_create(name=f"city{i}")
        countries.append(c)
    return countries


def create_actors():
    actors = []
    for i in range(1, 10):
        a, _ = catalog_m.Person.objects.get_or_create(
            first_name=f"first_name_actor{i}",
            last_name=f"last_name_actor{i}",
            type=catalog_c.PERSON_TYPE_ACTOR,
        )
        actors.append(a)
    return actors


def create_directors():
    directors = []
    for i in range(1, 4):
        d, _ = catalog_m.Person.objects.get_or_create(
            first_name=f"first_name_director{i}",
            last_name=f"last_name_director{i}",
            type=catalog_c.PERSON_TYPE_DIRECTOR,
        )
        directors.append(d)
    return directors


def create_genres():
    genres = []
    for i in range(1, 7):
        g, _ = catalog_m.MediaGenre.objects.get_or_create(name=f"genre{i}")
        genres.append(g)
    return genres


def create_developers():
    developers = []
    for i in range(1, 5):
        d, _ = catalog_m.Developer.objects.get_or_create(name=f"developer{i}")
        developers.append(d)
    return developers


def create_movies(countries, actors, directors, genres):
    for i in range(1, 10):
        m, _ = catalog_m.Movie.objects.get_or_create(
            title=f"movie{i}",
            description=f"movie{i}",
            release_date="2024-08-04",
            duration=timedelta(hours=2),
            country=choice(countries),
            avg_rating=5,
        )
        m.genres.set(sample(genres, 3))
        m.directors.set(sample(directors, 2))
        m.actors.set(sample(actors, 3))


def create_games(developers, genres):
    for i in range(1, 10):
        g, _ = catalog_m.Game.objects.get_or_create(
            title=f"game{i}",
            description=f"game{i}",
            release_date="2024-08-04",
            developer=choice(developers),
            avg_rating=5,
        )
        g.genres.set(sample(genres, 3))


def create_animes(directors, genres):
    for i in range(1, 10):
        a, _ = catalog_m.Anime.objects.get_or_create(
            title=f"anime{i}",
            description=f"anime{i}",
            release_date="2024-08-04",
            episodes=15,
            avg_rating=5,
        )
        a.genres.set(sample(genres, 3))
        a.directors.set(sample(directors, 2))


def create_series(countries, actors, directors, genres):
    for i in range(1, 10):
        s, _ = catalog_m.Series.objects.get_or_create(
            title=f"series{i}",
            description=f"series{i}",
            release_date="2024-08-04",
            country=choice(countries),
            episodes=15,
            avg_rating=5,
        )
        s.genres.set(sample(genres, 3))
        s.directors.set(sample(directors, 2))
        s.actors.set(sample(actors, 3))


if __name__ == "__main__":
    print("Creating data...")
    countries = create_countries()
    actors = create_actors()
    directors = create_directors()
    genres = create_genres()
    developers = create_developers()
    create_movies(countries, actors, directors, genres)
    create_animes(directors, genres)
    create_games(developers, genres)
    create_series(countries, actors, directors, genres)
    print("Done!")
