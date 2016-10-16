from django.db import models
from django.utils.translation import ugettext as _


class Zosia(models.Model):
    start_date = models.DateField(
        verbose_name=_('First day')
    )
    end_date = models.DateField(
        verbose_name=_('Last day')
    )

    active = models.BooleanField(
        default=False
    )

    place_name = models.CharField(
        max_length=300
    )
    place_url = models.CharField(
        max_length=300
    )
    place_address = models.TextField()

    banner = models.ImageField()

    def __str__(self):
        return 'In {} from {} to {}'.format(str(self.place_name),
                                            self.start_date,
                                            self.end_date)
