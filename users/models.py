from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)

    @property
    def display_name(self):
        full_name = self.get_full_name()
        return full_name or str(self)


class Organization(models.Model):
    name = models.CharField(
        max_length=300
    )
    accepted = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.name
