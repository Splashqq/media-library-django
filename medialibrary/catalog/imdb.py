import gzip
from datetime import timedelta
from io import BytesIO

import pandas as pd
import requests
from django.db import transaction

import medialibrary.catalog.models as catalog_m


def get_top_movies_ids_and_info(limit=10):
    rating_url = "https://datasets.imdbws.com/title.ratings.tsv.gz"
    ratings = {}

    with requests.get(rating_url, stream=True) as response:
        response.raise_for_status()
        with gzip.GzipFile(fileobj=BytesIO(response.content)) as gz_file:
            next(gz_file)
            for line in gz_file:
                tconst, avg_rating, num_votes = line.decode("utf-8").strip().split("\t")
                ratings[tconst] = {
                    "num_votes": int(num_votes),
                }

    url = "https://datasets.imdbws.com/title.basics.tsv.gz"
    movies = []
    columns = [
        "tconst",
        "primaryTitle",
        "runtimeMinutes",
        "genres",
    ]

    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with gzip.GzipFile(fileobj=BytesIO(response.content)) as gz_file:
            header = gz_file.readline().decode("utf-8").strip().split("\t")
            for line in gz_file:
                parts = line.decode("utf-8").strip().split("\t")
                record = dict(zip(header, parts))
                if record["tconst"] in ratings and record.get("titleType") == "movie":
                    movie_data = {
                        "tconst": record["tconst"],
                        "primaryTitle": record.get("primaryTitle", ""),
                        "runtimeMinutes": record.get("runtimeMinutes", ""),
                        "genres": record.get("genres", ""),
                        "num_votes": ratings[record["tconst"]]["num_votes"],
                    }
                    movies.append(movie_data)

    df = pd.DataFrame(movies, columns=columns).drop_duplicates("tconst")
    movies.sort(
        key=lambda x: x["num_votes"],
        reverse=True,
    )
    return [movie["tconst"] for movie in movies[:limit]], df


def get_staff_info(ids):
    url = "https://datasets.imdbws.com/title.principals.tsv.gz"
    ids_set = set(ids)
    results = []
    columns = ["tconst", "nconst", "category"]

    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with gzip.GzipFile(fileobj=BytesIO(response.content)) as gz_file:
            header = gz_file.readline().decode("utf-8").strip().split("\t")
            for line in gz_file:
                parts = line.decode("utf-8").strip().split("\t")
                record = dict(zip(header, parts))
                if record["tconst"] in ids_set:
                    results.append([record.get(col, None) for col in columns])

    return pd.DataFrame(results, columns=columns)


def get_people_info(staff_ids):
    url = "https://datasets.imdbws.com/name.basics.tsv.gz"
    staff_set = set(staff_ids)
    results = []
    columns = [
        "nconst",
        "primaryName",
    ]

    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with gzip.GzipFile(fileobj=BytesIO(response.content)) as gz_file:
            header = gz_file.readline().decode("utf-8").strip().split("\t")
            for line in gz_file:
                parts = line.decode("utf-8").strip().split("\t")
                record = dict(zip(header, parts))
                if record["nconst"] in staff_set:
                    results.append([record.get(col, None) for col in columns])
                    if len(results) >= len(staff_set):
                        break

    return pd.DataFrame(results, columns=columns).drop_duplicates("nconst")


def prepare_movie_data(movie_id, movies_basic, staff_info, people_info):
    movie = movies_basic[movies_basic["tconst"] == movie_id].iloc[0]
    genres = movie["genres"].split(",") if pd.notna(movie["genres"]) else []

    staff = []
    for _, staff_member in staff_info[staff_info["tconst"] == movie_id].iterrows():
        person = people_info[people_info["nconst"] == staff_member["nconst"]]
        if not person.empty:
            staff.append(
                {
                    "imdb_id": staff_member["nconst"],
                    "name": person.iloc[0]["primaryName"],
                    "role": staff_member["category"],
                }
            )

    duration = (
        timedelta(minutes=int(movie["runtimeMinutes"]))
        if pd.notna(movie["runtimeMinutes"]) and str(movie["runtimeMinutes"]).isdigit()
        else None
    )

    return {
        "imdb_id": movie_id,
        "title": movie["primaryTitle"],
        "duration": duration,
        "genres": genres,
        "staff": staff,
    }


def update_or_create_movies(movies_data):
    with transaction.atomic():
        imdb_ids = [m["imdb_id"] for m in movies_data]
        existing_movies = {
            m.imdb_id: m for m in catalog_m.Movie.objects.filter(imdb_id__in=imdb_ids)
        }

        all_genres = {g for m in movies_data for g in m.get("genres", [])}
        genres_map = {
            g.name: g for g in catalog_m.MediaGenre.objects.filter(name__in=all_genres)
        }
        new_genres = [
            catalog_m.MediaGenre(name=name)
            for name in all_genres
            if name not in genres_map
        ]
        if new_genres:
            catalog_m.MediaGenre.objects.bulk_create(new_genres)
            genres_map.update({g.name: g for g in new_genres})

        staff_members = {
            s["imdb_id"]: s["name"]
            for m in movies_data
            for s in m.get("staff", [])
            if s.get("imdb_id")
        }
        existing_persons = catalog_m.Person.objects.filter(
            imdb_id__in=staff_members.keys()
        ).in_bulk(field_name="imdb_id")
        persons_to_create = [
            catalog_m.Person(name=name, imdb_id=imdb_id)
            for imdb_id, name in staff_members.items()
            if imdb_id not in existing_persons
        ]
        if persons_to_create:
            catalog_m.Person.objects.bulk_create(
                persons_to_create, ignore_conflicts=True
            )
            existing_persons.update(
                catalog_m.Person.objects.filter(
                    imdb_id__in=[p.imdb_id for p in persons_to_create]
                ).in_bulk(field_name="imdb_id")
            )

        movies_to_create = []
        movies_to_update = []
        for m in movies_data:
            defaults = {
                "title": m["title"],
                "duration": m["duration"],
            }
            if m["imdb_id"] in existing_movies:
                movie = existing_movies[m["imdb_id"]]
                for attr, value in defaults.items():
                    setattr(movie, attr, value)
                movies_to_update.append(movie)
            else:
                movies_to_create.append(
                    catalog_m.Movie(imdb_id=m["imdb_id"], **defaults)
                )

        if movies_to_create:
            created_movies = catalog_m.Movie.objects.bulk_create(movies_to_create)
            existing_movies.update({m.imdb_id: m for m in created_movies})
        if movies_to_update:
            catalog_m.Movie.objects.bulk_update(
                movies_to_update, fields=["title", "duration"]
            )

        for m in movies_data:
            movie = existing_movies.get(m["imdb_id"])
            if movie and m.get("genres"):
                movie.genres.set(
                    [genres_map[g] for g in m["genres"] if g in genres_map]
                )

            if movie and m.get("staff"):
                role_names = {s["role"] for s in m["staff"]}
                existing_roles = {
                    r.name: r
                    for r in catalog_m.StaffRole.objects.filter(name__in=role_names)
                }
                new_roles = [
                    catalog_m.StaffRole(name=name)
                    for name in role_names
                    if name not in existing_roles
                ]
                if new_roles:
                    catalog_m.StaffRole.objects.bulk_create(new_roles)
                    existing_roles.update({r.name: r for r in new_roles})

                current_staff = set(
                    catalog_m.Staff.objects.filter(movie=movie).values_list(
                        "person__imdb_id", "role__name"
                    )
                )
                staff_to_create = []
                for s in m["staff"]:
                    if (
                        s.get("imdb_id")
                        and s["imdb_id"] in existing_persons
                        and s["role"] in existing_roles
                    ):
                        if (s["imdb_id"], s["role"]) not in current_staff:
                            staff_to_create.append(
                                catalog_m.Staff(
                                    person=existing_persons[s["imdb_id"]],
                                    movie=movie,
                                    role=existing_roles[s["role"]],
                                )
                            )
                if staff_to_create:
                    catalog_m.Staff.objects.bulk_create(staff_to_create)
