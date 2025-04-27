import tempfile
import uuid
from datetime import timedelta
from random import choice, sample

from django.core import mail
from django.core.cache import cache
from django.core.files import File
from django.test import override_settings
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

import medialibrary.catalog.models as catalog_m
import medialibrary.common.constants as common_c
import medialibrary.common.models as common_m
import medialibrary.users.constants as users_c
import medialibrary.users.models as users_m


class UserVSTestCase(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "email@gmail.com",
            "username": "username",
            "password": "password",
        }
        self.user = users_m.User.objects.create_user(**self.user_data)
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()

    def tearDown(self):
        cache.clear()

    def test_login_success(self):
        data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        }
        response = self.client.post("/api/users/user/login/", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)

    def test_login_invalid_credentials(self):
        data = {
            "email": self.user_data["email"],
            "password": "wrongpassword",
        }
        response = self.client.post("/api/users/user/login/", data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid credentials")

    def test_register_success(self):
        data = {
            "email": "register@gmail.com",
            "username": "register",
            "password1": "password",
            "password2": "password",
        }
        response = self.client.post("/api/users/user/register/", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertTrue(users_m.User.objects.filter(email=data["email"]).exists())

    def test_register_duplicate_email_and_username(self):
        data = {
            "email": self.user_data["email"],
            "username": "register",
            "password1": "password",
            "password2": "password",
        }
        response = self.client.post("/api/users/user/register/", data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            "email": "register@gmail.com",
            "username": self.user_data["username"],
            "password1": "password",
            "password2": "password",
        }
        response = self.client.post("/api/users/user/register/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_different_passwords(self):
        data = {
            "email": "register@gmail.com",
            "username": "register",
            "password1": "password1",
            "password2": "password2",
        }
        response = self.client.post("/api/users/user/register/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        data = {
            "old_password": self.user_data["password"],
            "new_password": "newpassword123",
            "confirm_password": "newpassword123",
        }
        response = self.client.post("/api/users/user/change_password/", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Password changed successfully")

    def test_change_password_unauthorized(self):
        data = {
            "old_password": self.user_data["password"],
            "new_password": "newpassword123",
        }
        response = self.client.post("/api/users/user/change_password/", data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reset_password_success(self):
        mail.outbox = []
        data = {"email": self.user_data["email"]}
        response = self.client.post("/api/users/user/reset_password/", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Message sent")
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, "Password reset message")
        self.assertEqual(email.to, [self.user.email])

    def test_reset_password_invalid_email(self):
        data = {"email": "nonexistent@example.com"}
        response = self.client.post("/api/users/user/reset_password/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_confirm_success(self):
        token = uuid.uuid4()
        cache_data = {
            "user_id": self.user.id,
            "temp_password": "temp_password",
            "email": self.user.email,
        }
        cache_key = f"password_reset_{token}"
        cache.set(cache_key, cache_data, timeout=600)

        response = self.client.get(f"/api/users/user/password-reset-confirm/{token}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Password was changed")

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("temp_password"))

    def test_reset_password_confirm_invalid_token(self):
        invalid_token = "00000000-0000-0000-0000-000000000000"
        response = self.client.get(
            f"/api/users/user/password-reset-confirm/{invalid_token}/"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid or expired token")

    def test_update_profile_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        data = {"username": "new_username"}
        response = self.client.patch(f"/api/users/user/{self.user.pk}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "new_username")

    def test_update_other_user_profile(self):
        other_user = users_m.User.objects.create_user(
            email="other@example.com", username="otheruser", password="otherpass123"
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        data = {"username": "trytochange"}
        response = self.client.patch(f"/api/users/user/{other_user.id}/", data=data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["detail"], "Can't edit profile")

    def test_reset_password_rate_limiting(self):
        data = {"email": self.user_data["email"]}

        response = self.client.post("/api/users/user/reset_password/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post("/api/users/user/reset_password/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


TEMP_MEDIA = tempfile.mktemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class TestUserMovieCollectionVS(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "email@gmail.com",
            "username": "username",
            "password": "password",
        }
        self.user = users_m.User.objects.create_user(**self.user_data)
        self.token = Token.objects.create(user=self.user)
        self.movie = catalog_m.Movie.objects.create(
            imdb_id="tt00000",
            title="Test Movie",
            description="Test Movie Description",
        )
        self.movie_collection = users_m.UserMovieCollection.objects.create(
            user=self.user,
            movie=self.movie,
            status=users_c.USER_MEDIA_COLLECTION_STATUS_IN_PROGRESS,
        )
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
            users_m.UserMovieCollection.objects.create(
                user=choice(self.users),
                movie=movie,
                status=choice(users_c.USER_MEDIA_COLLECTION_STATUSES)[0],
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

    def test_list_retrieve_movies_collections_anonymous(self):
        response = self.client.get("/api/users/movie_collection/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            f"/api/users/movie_collection/{self.movie_collection.pk}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_put_patch_delete_movies_collections_anonymous(self):
        movie3 = catalog_m.Movie.objects.create(
            imdb_id="tt000003",
            title="Test Movie",
            description="Test Movie Description",
        )
        data = {
            "user": self.user,
            "movie": movie3.pk,
            "status": users_c.USER_MEDIA_COLLECTION_STATUS_IN_PROGRESS,
        }
        response = self.client.post("/api/users/movie_collection/", data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

        response = self.client.put("/api/users/movie_collection/", data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

        response = self.client.patch("/api/users/movie_collection/", data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

        response = self.client.delete("/api/users/movie_collection/", data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

    def test_get_list_movies_collections(self):
        response = self.client.get("/api/users/movie_collection/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data["results"], list)

    def test_get_retrieve_movies_collections(self):
        response = self.client.get(
            f"/api/users/movie_collection/{self.movie_collection.pk}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)

    def test_post_movies_collections(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        movie2 = catalog_m.Movie.objects.create(
            imdb_id="tt000001",
            title="Test Movie",
            description="Test Movie Description",
        )
        data = {
            "user": self.user,
            "movie": movie2.pk,
            "status": users_c.USER_MEDIA_COLLECTION_STATUS_IN_PROGRESS,
        }
        response = self.client.post("/api/users/movie_collection/", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_movies_collections_movie_duplicate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        data = {
            "user": self.user,
            "movie": self.movie.pk,
            "status": users_c.USER_MEDIA_COLLECTION_STATUS_IN_PROGRESS,
        }
        response = self.client.post("/api/users/movie_collection/", data=data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["detail"], "Movie already exists in collection")

    def test_put_movies_collections(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        movie2 = catalog_m.Movie.objects.create(
            imdb_id="tt000001",
            title="Test Movie",
            description="Test Movie Description",
        )
        data = {
            "user": self.user,
            "movie": movie2.pk,
            "status": users_c.USER_MEDIA_COLLECTION_STATUS_IN_PROGRESS,
        }
        response = self.client.put(
            f"/api/users/movie_collection/{self.movie_collection.pk}/", data=data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_movies_collections(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        data = {
            "user": self.user,
            "movie": self.movie.pk,
            "status": users_c.USER_MEDIA_COLLECTION_STATUS_WATCHED,
        }
        response = self.client.put(
            f"/api/users/movie_collection/{self.movie_collection.pk}/", data=data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_movies_collections(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.delete(
            f"/api/users/movie_collection/{self.movie_collection.pk}/",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_delete_other_user_movies_collections(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        user_data = {
            "email": "email2@gmail.com",
            "username": "username2",
            "password": "password",
        }
        user = users_m.User.objects.create_user(**user_data)
        movie = catalog_m.Movie.objects.create(
            imdb_id="tt00005",
            title="Test Movie",
            description="Test Movie Description",
        )
        movie_collection = users_m.UserMovieCollection.objects.create(
            user=user,
            movie=movie,
            status=users_c.USER_MEDIA_COLLECTION_STATUS_IN_PROGRESS,
        )
        data = {"status": users_c.USER_MEDIA_COLLECTION_STATUS_ABANDONED}

        response = self.client.patch(
            f"/api/users/movie_collection/{movie_collection.pk}/", data=data
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["detail"], "Can't edit collection")

        response = self.client.delete(
            f"/api/users/movie_collection/{movie_collection.pk}/"
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["detail"], "Can't delete collection")

    def test_queries(self):
        # 2 - select movies_collections with pagination
        # 2 - select photo, videos
        # 3 - select movies, staff, genres
        with self.assertNumQueries(7):
            response = self.client.get("/api/users/movie_collection/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
