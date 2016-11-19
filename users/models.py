from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)


class Organization(models.Model):
    name = models.CharField(
        max_length=300
    )
    accepted = models.BooleanField(
        default=False
    )
