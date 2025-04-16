import uuid

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

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
