from django.db import models
from django.utils.translation import ugettext_lazy as _


class QA(models.Model):
    question = models.CharField(verbose_name=_('Question'), max_length=150)
    answer = models.CharField(verbose_name=_('Answer'), max_length=500)
    priority = models.PositiveSmallIntegerField(
        verbose_name=_('Priority'),
        default=0,
        help_text=_('Questions are sorted in descending order of priorities')
    )
