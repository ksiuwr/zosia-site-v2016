from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Organization(models.Model):
    name = models.CharField(
        max_length=300
    )
    accepted = models.BooleanField(
        default=False
    )
