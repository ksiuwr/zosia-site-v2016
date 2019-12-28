from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import User


class Boardgame(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=200)
    votes = models.PositiveSmallIntegerField(default=0)

    ACCEPTED = "A"
    SUGGESTED = "S"
    STATE_OF_BOARDGAME_CHOICES = [
        (ACCEPTED, "accepted"), (SUGGESTED, "suggested")]
    state = models.CharField(
        max_length=1,
        choices=STATE_OF_BOARDGAME_CHOICES,
        default=SUGGESTED,
    )
    
    class Meta:
        ordering = ["state", "-votes"]

    def __str__(self):
        return self.name
