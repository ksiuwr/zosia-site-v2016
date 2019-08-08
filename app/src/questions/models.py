from django.db import models
from django.utils.translation import ugettext_lazy as _


class QA(models.Model):
    question = models.CharField(_('Question'), max_length=150)
    answer = models.CharField(_('Answer'), max_length=500)
