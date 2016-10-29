from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Organization(models.Model):
    name = models.CharField(
        max_length=300
    )
    accepted = models.BooleanField(
        default=False
    )
