from django.db import models
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from datetime import timedelta


class Place(models.Model):
    name = models.CharField(
        max_length=300
    )
    url = models.URLField(
        max_length=300,
        blank=True
    )
    address = models.TextField()

    def __str__(self):
        return self.name


class ZosiaManager(models.Manager):
    def find_active(self):
        return self.filter(active=True).first()

# NOTE: Zosia has 4 days. Period.
class Zosia(models.Model):
    objects = ZosiaManager()

    start_date = models.DateField(
        verbose_name=_('First day')
    )

    active = models.BooleanField(
        default=False
    )

    banner = models.ImageField(blank=True, null=True)

    place = models.ForeignKey(Place)

    @property
    def end_date(self):
        return start_date + timedelta(3)

    def __str__(self):
        return 'Zosia {}'.format(self.start_date.year)

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError(
                _('Zosia has to have non-negative duration')
            )
        super(Zosia, self).clean()

    def validate_unique(self, **kwargs):
        # NOTE: If this instance is not yet saved, self.pk == None
        # So this query will take all active objects from db
        if self.active and Zosia.objects.exclude(pk=self.pk).filter(active=True).exists():
            raise ValidationError(
                _('Only one Zosia may be active at any given time')
            )
        super(Zosia, self).validate_unique(**kwargs)


class Bus(models.Model):
    zosia = models.ForeignKey(Zosia)
    capacity = models.IntegerField()
    time = models.TimeField()


class UserPrefences(models.Model):
    user = models.ForeignKey(User)
    zosia = models.ForeignKey(Zosia)
    organization = models.ForeignKey(Organization)
    bus = models.ForeignKey(Bus, null=True, blank=True)

