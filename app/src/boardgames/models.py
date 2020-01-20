from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import User


class Boardgame(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=200)
    votes_amount = models.PositiveSmallIntegerField(default=0)

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
        ordering = ["state", "-votes_amount"]

    def __str__(self):
        return self.name

    def votes_up(self):
        self.votes_amount += 1
        # return self.votes_amount

    def votes_down(self):
        self.votes_amount -= 1
        # return self.votes_amount

    def accept_boardgame(self):
        self.state = "A"
        return self.state


class Vote(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE)
    boardgame = models.ForeignKey(
        Boardgame,
        on_delete = models.CASCADE
    )

    def change_votes():
        pass
