from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from conferences.models import Zosia
from utils.constants import DURATION_CHOICES, LECTURE_TYPE, LectureInternals, PERSON_TYPE


class Lecture(models.Model):
    # organizational informations
    zosia = models.ForeignKey(Zosia, verbose_name=_("Conference"), on_delete=models.CASCADE)
    requests = models.CharField(
        verbose_name=_("Requests or comments"), max_length=800, blank=True, null=True,
        help_text=_("Your requests, suggestions or comments intended for organizers"))

    create_date = models.DateTimeField(verbose_name=_("Creation date"), auto_now_add=True)
    accepted = models.BooleanField(verbose_name=_("Accepted"), default=False)
    priority = models.IntegerField(default=99, help_text=_("Set order on all lectures page"))

    # main data about lecture
    title = models.CharField(verbose_name=_("Title"), max_length=256)
    abstract = models.CharField(verbose_name=_("Abstract"), max_length=2048)
    duration = models.PositiveSmallIntegerField(
        choices=DURATION_CHOICES,
        verbose_name=_("Duration (in minutes)"),
        help_text=_("Please remember that organizers <u>ARE ALLOWED</u> to cut you off during your "
                    "lecture or workshop when you're out of declared time!")
    )
    lecture_type = models.CharField(verbose_name=_("Type"), max_length=1, choices=LECTURE_TYPE)
    events = models.CharField(
        verbose_name=_("Additional events"), max_length=800, blank=True, null=True,
        help_text=_(
            "Are you planning any event after your lecture or workshop (e.g. pizza, drinks, "
            "games, recruitment)? <b>TELL US ABOUT IT!</b> Beware that organizers <u>WON'T ALLOW</u> "
            "you to arrange your event if you don't announce it here!")
    )

    # about author
    person_type = models.CharField(verbose_name=_("Person type"), max_length=1, choices=PERSON_TYPE,
                                   default=LectureInternals.PERSON_NORMAL)
    description = models.CharField(verbose_name=_("Author description"), max_length=256, null=True,
                                   blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Author"),
                               on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.author, self.title)

    class Meta:
        verbose_name = _("Lecture")
        verbose_name_plural = _("Lectures")
        ordering = ['priority', 'id']

    def toggle_accepted(self):
        self.accepted = not self.accepted
        self.save()

    def clean(self):
        if self.duration is None:
            return

        lecture_max_time = 90 if self.person_type == LectureInternals.PERSON_SPONSOR else 60
        workshop_min_time = 30

        if self.lecture_type == LectureInternals.TYPE_LECTURE and self.duration > lecture_max_time:
            raise ValidationError({
                "duration": ValidationError(
                    _("Lecture is too long, maximal time for you is %(time)s minutes"),
                    code="invalid",
                    params={"time": lecture_max_time}
                )
            })

        if self.lecture_type == LectureInternals.TYPE_WORKSHOP and self.duration < workshop_min_time:
            raise ValidationError({
                "duration": ValidationError(
                    _("Workshop is too short, minimal time is %(time)s minutes"),
                    code="invalid",
                    params={"time": workshop_min_time}
                )
            })


class Schedule(models.Model):
    zosia = models.ForeignKey(Zosia, verbose_name=_("Conference"), on_delete=models.CASCADE)
    content = models.TextField(verbose_name=_("content"),
                               help_text=_("You can use html tags and materializecss classes"))
