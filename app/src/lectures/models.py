from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from conferences.models import Zosia
from .constants import DURATION_CHOICES, LECTURE_TYPE, PERSON_TYPE


class Lecture(models.Model):
    # organizational informations
    zosia = models.ForeignKey(Zosia, verbose_name=_("Conference"), on_delete=models.CASCADE)
    info = models.CharField(verbose_name=_("Information"), max_length=800,
                            help_text=_("Your suggestions, requests and "
                                        "comments intended for organizers and"
                                        " a lot more,"), blank=True, null=True)
    create_date = models.DateTimeField(verbose_name="Creation date",
                                       auto_now_add=True)
    accepted = models.BooleanField(verbose_name=_("Accepted"), default=False)
    priority = models.IntegerField(default=99, help_text=_("Set order on all lectures page"))
    # main data about lecture
    title = models.CharField(verbose_name=_("Title"), max_length=256)
    abstract = models.CharField(verbose_name=_("Abstract"), max_length=2048)
    duration = models.CharField(verbose_name=_("Duration"), max_length=3,
                                choices=DURATION_CHOICES)
    lecture_type = models.CharField(verbose_name=_("Type"), max_length=1,
                                    choices=LECTURE_TYPE)
    # about author
    person_type = models.CharField(verbose_name=_("Person type"), max_length=1,
                                   choices=PERSON_TYPE)
    description = models.CharField(verbose_name=_("Author description"),
                                   max_length=256, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               verbose_name=_("Author"),
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


class Schedule(models.Model):
    zosia = models.ForeignKey(Zosia, verbose_name=_("Conference"), on_delete=models.CASCADE)
    content = models.TextField(verbose_name=_("content"),
                               help_text=_("You can use html tags and materializecss classes"))
