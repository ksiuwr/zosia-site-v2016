from django.db import models
from django.utils.translation import ugettext_lazy as _


class Sponsor(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=200, unique=True)
    is_active = models.BooleanField(verbose_name=_("Active"), default=False)
    url = models.URLField(verbose_name=_("URL"), max_length=200, blank=True,
                          null=True)
    logo = models.ImageField(verbose_name=_("Logo"), upload_to='sponsors')

    def __str__(self):
        return self.name

    def toggle_active(self):
        self.is_active = not self.is_active
