import tempfile
from datetime import timedelta
from random import choice, sample

from django.core.files import File
from django.test import override_settings
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

import medialibrary.catalog.models as catalog_m
import medialibrary.common.constants as common_c
import medialibrary.common.models as common_m
import medialibrary.users.models as users_m

TEMP_MEDIA = tempfile.mktemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class TestMovieVS(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "email@gmail.com",
            "username": "username",
            "password": "password",
        }
        self.user = users_m.User.objects.create_user(**self.user_data)
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()

        self.users = []
        for i in range(1, 5):
            user = users_m.User.objects.create_user(
                email=f"emaill{i}@gmail.com",
                username=f"usernamee{i}",
                password="password",
            )
            self.users.append(user)

        self.companies = []
        for i in range(1, 4):
            company = catalog_m.Company.objects.create(name=f"name{i}")
            self.companies.append(company)

        self.genres = []
        for i in range(1, 5):
            genre = catalog_m.MediaGenre.objects.create(name=f"genre{i}")
            self.genres.append(genre)

        self.persons = []
        for i in range(1, 10):
            person = catalog_m.Person.objects.create(
                name=f"name{i}",
            )
            self.persons.append(person)

        self.staff_roles = []
        for i in range(1, 5):
            staff_role = catalog_m.StaffRole.objects.create(
                name=f"staff_role{i}",
            )
            self.staff_roles.append(staff_role)

        self.movies = []
        for i in range(1, 5):
            movie = catalog_m.Movie.objects.create(
                imdb_id=f"tt{i}",
                title=f"Test Movie {i}",
                description=f"Test Movie Description {i}",
                release_date="2024-08-04",
                duration=timedelta(hours=2),
                company=choice(self.companies),
            )
            movie.genres.set(sample(self.genres, 2))

            for j in range(1, 3):
                catalog_m.Staff.objects.create(
                    person=self.persons[i],
                    movie=movie,
                    role=choice(self.staff_roles),
                )
            self.movies.append(movie)

        with open("medialibrary/utils/test_data/photo.png", "rb") as f:
            for movie in self.movies:
                poster = common_m.Photo.objects.create(
                    photo=File(f),
                    type=common_c.PHOTO_TYPE_POSTER,
                    movie=movie,
                )
                movie.poster = poster

                for _ in range(5):
                    common_m.Photo.objects.create(
                        photo=File(f),
                        type=common_c.PHOTO_TYPE_MOVIE_PHOTOS,
                        movie=movie,
                    )

                with open("medialibrary/utils/test_data/video.mp4", "rb") as f2:
                    common_m.Video.objects.create(
                        video=File(f2),
                        type=common_c.VIDEO_TYPE_TRAILER,
                        movie=movie,
                        preview=poster,
                    )

            user_avatar = common_m.Photo.objects.create(
                photo=File(f), type=common_c.PHOTO_TYPE_USER_AVATAR
            )
            for user in self.users:
                user.avatar = user_avatar
                user.save()

        self.series = []
        for i in range(1, 5):
            series = catalog_m.Series.objects.create(
                title=f"Test Series {i}",
                description=f"Test Series Description {i}",
                release_date="2024-08-04",
                episode_duration=timedelta(minutes=20),
                company=choice(self.companies),
                episodes=12,
            )
            series.genres.set(sample(self.genres, 2))

            for j in range(1, 3):
                catalog_m.Staff.objects.create(
                    person=self.persons[i],
                    series=series,
                    role=choice(self.staff_roles),
                )
            self.series.append(series)

        with open("medialibrary/utils/test_data/photo.png", "rb") as f:
            for series in self.series:
                poster = common_m.Photo.objects.create(
                    photo=File(f),
                    type=common_c.PHOTO_TYPE_POSTER,
                    series=series,
                )
                series.poster = poster

                for _ in range(5):
                    common_m.Photo.objects.create(
                        photo=File(f),
                        type=common_c.PHOTO_TYPE_SERIES_PHOTOS,
                        series=series,
                    )

                with open("medialibrary/utils/test_data/video.mp4", "rb") as f2:
                    common_m.Video.objects.create(
                        video=File(f2),
                        type=common_c.VIDEO_TYPE_TRAILER,
                        series=series,
                        preview=poster,
                    )

        self.games = []
        for i in range(1, 5):
            game = catalog_m.Game.objects.create(
                title=f"Test Game {i}",
                description=f"Test Game Description {i}",
                release_date="2024-08-04",
                company=choice(self.companies),
            )
            game.genres.set(sample(self.genres, 2))

            self.games.append(game)

        with open("medialibrary/utils/test_data/photo.png", "rb") as f:
            for game in self.games:
                poster = common_m.Photo.objects.create(
                    photo=File(f),
                    type=common_c.PHOTO_TYPE_POSTER,
                    game=game,
                )
                game.poster = poster

                for _ in range(5):
                    common_m.Photo.objects.create(
                        photo=File(f),
                        type=common_c.PHOTO_TYPE_GAME_PHOTOS,
                        game=game,
                    )

                with open("medialibrary/utils/test_data/video.mp4", "rb") as f2:
                    common_m.Video.objects.create(
                        video=File(f2),
                        type=common_c.VIDEO_TYPE_TRAILER,
                        game=game,
                        preview=poster,
                    )

    def test_get_list_movies(self):
        response = self.client.get("/api/catalog/movie/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data["results"], list)

    def test_get_retrieve_movies(self):
        response = self.client.get(f"/api/catalog/movie/{self.movies[0].pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)

    def test_queries_movies(self):
        # 2 - select movies with pagination
        # 2 - select photo, videos
        # 2 - select staff, genres
        with self.assertNumQueries(6):
            response = self.client.get("/api/catalog/movie/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list_series(self):
        response = self.client.get("/api/catalog/series/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data["results"], list)

    def test_get_retrieve_series(self):
        response = self.client.get(f"/api/catalog/series/{self.series[0].pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)

    def test_queries_series(self):
        # 2 - select series with pagination
        # 2 - select photo, videos
        # 2 - select staff, genres
        with self.assertNumQueries(6):
            response = self.client.get("/api/catalog/series/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list_games(self):
        response = self.client.get("/api/catalog/game/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data["results"], list)

    def test_get_retrieve_games(self):
        response = self.client.get(f"/api/catalog/game/{self.series[0].pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)

    def test_queries_games(self):
        # 2 - select game with pagination
        # 2 - select photo, videos
        # 1 - select genres
        with self.assertNumQueries(5):
            response = self.client.get("/api/catalog/game/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
