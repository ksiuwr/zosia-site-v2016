from django.db import models
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from datetime import timedelta

from users.models import User, Organization
from conferences.constants import SHIRT_SIZE_CHOICES, SHIRT_TYPES_CHOICES


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
    description = models.TextField(default='')

    @property
    def end_date(self):
        return self.start_date + timedelta(3)

    def __str__(self):
        return 'Zosia {}'.format(self.start_date.year)

    def validate_unique(self, **kwargs):
        # NOTE: If this instance is not yet saved, self.pk == None
        # So this query will take all active objects from db
        if self.active and Zosia.objects.exclude(pk=self.pk).filter(active=True).exists():
            raise ValidationError(
                _(u'Only one Zosia may be active at any given time')
            )
        super(Zosia, self).validate_unique(**kwargs)


class Bus(models.Model):
    zosia = models.ForeignKey(Zosia)
    capacity = models.IntegerField()
    time = models.TimeField()


class UserPreferences(models.Model):
    user = models.ForeignKey(User)
    zosia = models.ForeignKey(Zosia)
    organization = models.ForeignKey(Organization)
    bus = models.ForeignKey(Bus, null=True, blank=True)

    # Day 1 (Coming)
    accomodation_day_1 = models.BooleanField()
    dinner_1 = models.BooleanField()

    # Day 2 (Regular day)
    accomodation_day_2 = models.BooleanField()
    breakfast_2 = models.BooleanField()
    dinner_2 = models.BooleanField()

    # Day 3 (Regular day)
    accomodation_day_3 = models.BooleanField()
    breakfast_3 = models.BooleanField()
    dinner_3 = models.BooleanField()

    # Day 4 (Return)
    breakfast_4 = models.BooleanField()

    # Misc
    # Mobile, facebook, google+, whatever - always handy when someone forgets to wake up.
    contact = models.TextField()
    vegetarian = models.BooleanField()
    # Set by admin after checking payment
    payment_accepted = models.BooleanField(default=False)

    shirt_size = models.CharField(max_length=5, choices=SHIRT_SIZE_CHOICES)
    shirt_type = models.CharField(max_length=1, choices=SHIRT_TYPES_CHOICES)

    # Assigned by admin for various reasons (early registration / payment, help, etc)
    # Should allow some users to book room earlier
    # Typically, almost everyone has some bonus, so we don't get trampled
    # by wave of users booking room at the same time
    bonus_minutes = models.IntegerField(default=0)
