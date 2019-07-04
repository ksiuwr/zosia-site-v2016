from datetime import datetime, timedelta

from django.db import models
from django.db.models import Count, F
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError

from conferences.constants import SHIRT_SIZE_CHOICES, SHIRT_TYPES_CHOICES
from users.models import Organization, User

from pytz import timezone


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
    class Meta:
        verbose_name = 'Conference'
        verbose_name_plural = 'Conferences'

    objects = ZosiaManager()

    start_date = models.DateField(
        verbose_name=_('First day')
    )
    active = models.BooleanField(
        default=False
    )
    banner = models.ImageField(blank=True, null=True)
    place = models.ForeignKey(Place, on_delete=models.PROTECT)
    description = models.TextField(default='')

    registration_start = models.DateField(
        verbose_name=_('Registration for users starts'),
    )
    registration_end = models.DateField()

    rooming_start = models.DateField(
        verbose_name=_('Users room picking starts'),
    )
    rooming_end = models.DateField()

    lecture_registration_start = models.DateField(
        verbose_name=_('Registration for lectures starts'),
    )
    lecture_registration_end = models.DateField()

    price_accomodation = models.IntegerField(
        verbose_name=_('Price for sleeping in hotel, per day'),
    )
    price_accomodation_breakfast = models.IntegerField(
        verbose_name=_('Price for accomodation + breakfast'),
    )
    price_accomodation_dinner = models.IntegerField(
        verbose_name=_('Price for accomodation + dinner'),
    )
    price_whole_day = models.IntegerField(
        verbose_name=_('Price for whole day (accomodation + breakfast + dinner)'),
    )
    price_transport = models.IntegerField(
        verbose_name=_('Price for transportation')
    )
    price_base = models.IntegerField(
        verbose_name=_('Organisation fee'),
        default=0)

    account_number = models.CharField(
        max_length=32,
        verbose_name=_('Organization account for paying'),
    )
    account_details = models.TextField(
        verbose_name=_('Details for account (name, address)'),
        default='',
    )

    @property
    def end_date(self):
        return self.start_date + timedelta(3)

    def __str__(self):
        return 'Zosia {}'.format(self.start_date.year)

    @property
    def is_rooming_open(self):
        # XXX: bonuses will not work, because they subtract time from
        # the T0 `rooming_start` date, meaning that the below condition will
        # be fulfilled for everyone at the same time, exactly at the rooming_start
        # return self.rooming_start <= datetime.now().date() <= self.rooming_end
        return datetime.now().date() <= self.rooming_end

    def can_start_rooming(self, user, now=None):
        if now is None:
            now = datetime.now()
        return user.payment_accepted and now >= user.convert_bonus_to_time()

    def validate_unique(self, **kwargs):
        # NOTE: If this instance is not yet saved, self.pk == None
        # So this query will take all active objects from db
        if self.active and Zosia.objects.exclude(pk=self.pk).filter(active=True).exists():
            raise ValidationError(
                _(u'Only one Zosia may be active at any given time')
            )
        super(Zosia, self).validate_unique(**kwargs)

    @property
    def is_lectures_open(self):
        now = datetime.now().date()
        return self.lecture_registration_start <= now <= self.lecture_registration_end


class BusManager(models.Manager):
    def find_with_free_places(self, zosia):
        return self \
                .filter(zosia=zosia) \
                .annotate(seats_taken=Count('userpreferences')). \
                filter(capacity__gt=F('seats_taken'))


class Bus(models.Model):
    class Meta:
        verbose_name_plural = 'Buses'
    objects = BusManager()

    zosia = models.ForeignKey(Zosia, related_name='buses', on_delete=models.CASCADE)
    capacity = models.IntegerField()
    time = models.TimeField()
    name = models.TextField(default="Bus")

    def __str__(self):
        return str('{} {}'.format(self.name, self.time))

    @property
    def free_seats(self):
        return self.capacity - self.taken

    @property
    def taken(self):
        return UserPreferences.objects.filter(bus=self).count()


class UserPreferencesManager(models.Manager):
    def for_zosia(self, zosia, **override):
        defaults = {
            'zosia': zosia
        }
        defaults.update(**override)
        return self.filter(**defaults)


class UserPreferences(models.Model):
    class Meta:
        verbose_name_plural = 'Users preferences'

    objects = UserPreferencesManager()

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    zosia = models.ForeignKey(Zosia, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)
    # NOTE: Deleting bus will render some payment information inaccessible
    # (i.e. user chose transport -> user paid for it, transport is deleted, what now?)
    bus = models.ForeignKey(Bus, null=True, blank=True, on_delete=models.SET_NULL)

    # Day 1 (Coming)
    accomodation_day_1 = models.BooleanField(default=False)
    dinner_1 = models.BooleanField(default=False)

    # Day 2 (Regular day)
    accomodation_day_2 = models.BooleanField(default=False)
    breakfast_2 = models.BooleanField(default=False)
    dinner_2 = models.BooleanField(default=False)

    # Day 3 (Regular day)
    accomodation_day_3 = models.BooleanField(default=False)
    breakfast_3 = models.BooleanField(default=False)
    dinner_3 = models.BooleanField(default=False)

    # Day 4 (Return)
    breakfast_4 = models.BooleanField(default=False)

    # Misc
    # Mobile, facebook, google+, whatever - always handy when someone forgets to wake up.
    contact = models.TextField(default='', help_text='For example your phone number')
    information = models.TextField(
        default='', blank=True,
        help_text=_('Here is where you can give us information about yourself '
                    'that may be important during your trip.'))
    vegetarian = models.BooleanField(default=False)
    # Set by admin after checking payment
    payment_accepted = models.BooleanField(default=False)

    shirt_size = models.CharField(max_length=5, choices=SHIRT_SIZE_CHOICES, default=SHIRT_SIZE_CHOICES[0][0])
    shirt_type = models.CharField(max_length=1, choices=SHIRT_TYPES_CHOICES, default=SHIRT_TYPES_CHOICES[0][0])

    # Assigned by admin for various reasons (early registration / payment, help, etc)
    # Should allow some users to book room earlier
    # Typically, almost everyone has some bonus, so we don't get trampled
    # by wave of users booking room at the same time
    bonus_minutes = models.IntegerField(default=0)

    def _pays_for(self, option_name):
        return getattr(self, option_name)

    def _price_for(self, option_name):
        breakfast_price = self.zosia.price_accomodation_breakfast - self.zosia.price_accomodation
        dinner_price = self.zosia.price_accomodation_dinner - self.zosia.price_accomodation
        return {
            'accomodation_day_1': self.zosia.price_accomodation,
            'dinner_1': dinner_price,
            'breakfast_2': breakfast_price,
            'accomodation_day_2': self.zosia.price_accomodation,
            'dinner_2': dinner_price,
            'breakfast_3': breakfast_price,
            'accomodation_day_3': self.zosia.price_accomodation,
            'dinner_3': dinner_price,
            'breakfast_4': breakfast_price
        }[option_name]

    @property
    def price(self):
        payment = self.zosia.price_base

        payment_groups = [
            ['accomodation_day_1', 'dinner_1', 'breakfast_2'],
            ['accomodation_day_2', 'dinner_2', 'breakfast_3'],
            ['accomodation_day_3', 'dinner_3', 'breakfast_4'],
        ]

        if self.bus:
            payment += self.zosia.price_transport

        for group in payment_groups:
            if all(map(lambda d: self._pays_for(d), group)):
                payment += self.zosia.price_whole_day
            else:
                for g in group:
                    if self._pays_for(g):
                        payment += self._price_for(g)

        return payment

    def __str__(self):
        return str(self.user) + " preferences"

    def toggle_payment_accepted(self):
        self.payment_accepted = not self.payment_accepted
        return self.payment_accepted

    @property
    def room(self):
        return self.user.room_set.for_zosia(self.zosia).first()

    def convert_bonus_to_time(self):
        opening_time = datetime.combine(self.zosia.rooming_start, datetime.min.time())
        return opening_time - timedelta(0, 3*60*self.bonus_minutes)

    @property
    def rooming_time(self):
        return self.convert_bonus_to_time() \
                .astimezone(timezone('Europe/Warsaw')) \
                .strftime("%d.%m.%Y %H:%M")
