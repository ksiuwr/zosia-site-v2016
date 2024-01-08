from datetime import timedelta
import re

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Count, F, Q
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from utils.constants import DELIMITER, MAX_BONUS_MINUTES, RoomingStatus, UserInternals
from utils.time_manager import format_in_zone, now


class Place(models.Model):
    name = models.CharField(max_length=300)
    url = models.URLField(max_length=300, blank=True)
    address = models.TextField()
    town = models.CharField(max_length=60, help_text=_("Town displayed in terms and conditions"),
                            default="")

    def __str__(self):
        return self.name


class ZosiaManager(models.Manager):
    def find_active(self):
        return self.filter(active=True).first()

    def find_active_or_404(self):
        zosia = self.find_active()

        if zosia is None:
            raise Http404("No active conference found")

        return zosia


def validate_iban(value):
    iban_reg = r'^(PL)?(\d{2}[ ]\d{4}[ ]\d{4}[ ]\d{4}[ ]\d{4}[ ]\d{4}[ ]\d{4}|\d{26})$'
    m = re.match(iban_reg, value)
    if not m:
        raise ValidationError(_('This is not a valid Polish IBAN number'))
    # @formatter:off
    # https://pl.wikipedia.org/wiki/Mi%C4%99dzynarodowy_numer_rachunku_bankowego#Sprawdzanie_i_wyliczanie_cyfr_kontrolnych
    # @formatter:on
    iban = m.group(2).replace(" ", "")
    t = iban[2:] + "2521" + iban[:2]  # PL = 25 21
    res = 0
    for i in range(0, len(t)):
        res = (res * 10 + int(t[i])) % 97

    if res != 1:
        raise ValidationError(_(
            'This is not a valid Polish IBAN number: wrong checksum. Please check your bank '
            'account number!'
        ))


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
    place = models.ForeignKey(Place, related_name='conferences', on_delete=models.PROTECT)
    description = models.TextField(default='')

    registration_suspended = models.BooleanField(
        verbose_name=_('Is registration suspended'), default=False
    )

    early_registration_start = models.DateTimeField(
        verbose_name=_('Registration for early registering users starts'), null=True, blank=True
    )
    registration_start = models.DateTimeField(
        verbose_name=_('Registration for users starts'),
    )
    registration_end = models.DateTimeField()

    lecture_registration_start = models.DateTimeField(
        verbose_name=_('Registration for lectures starts'),
    )
    lecture_registration_end = models.DateTimeField()

    rooming_start = models.DateTimeField(
        verbose_name=_('Users room picking starts'),
    )
    rooming_end = models.DateTimeField()

    price_accommodation = models.IntegerField(
        verbose_name=_('Price for sleeping in hotel, per day'),
    )
    price_accommodation_breakfast = models.IntegerField(
        verbose_name=_('Price for accommodation + breakfast'),
    )
    price_accommodation_dinner = models.IntegerField(
        verbose_name=_('Price for accommodation + dinner'),
    )
    price_whole_day = models.IntegerField(
        verbose_name=_('Price for whole day (accommodation + breakfast + dinner)'),
    )
    price_transport = models.IntegerField(
        verbose_name=_('Price for transportation')
    )
    price_transport_with_discount = models.IntegerField(
        verbose_name=_('Price for transportation with discount'),
        default=0
    )
    price_transport_baggage = models.IntegerField(
        verbose_name=_('Price for transport baggage'),
        default=0
    )
    price_base = models.IntegerField(
        verbose_name=_('Organisation fee'),
        default=0
    )

    first_discount = models.IntegerField(
        verbose_name=_('First discount per day'),
        default=0
    )
    first_discount_limit = models.IntegerField(
        verbose_name=_('Limited number of registered users for first discount'),
        default=0
    )
    second_discount = models.IntegerField(
        verbose_name=_('Second discount per day'),
        default=0
    )
    second_discount_limit = models.IntegerField(
        verbose_name=_('Limited number of registered users for second discount'),
        default=0
    )
    third_discount = models.IntegerField(
        verbose_name=_('Third discount per day'),
        default=0
    )
    third_discount_limit = models.IntegerField(
        verbose_name=_('Limited number of registered users for third discount'),
        default=0
    )

    account_number = models.CharField(
        max_length=34,
        validators=[validate_iban],
        verbose_name=_('Organization account for paying')
    )
    account_owner = models.TextField(
        max_length=100,
        verbose_name=_('Account owner name')
    )
    account_bank = models.TextField(
        max_length=50,
        verbose_name=_('Bank name where account has been opened')
    )
    account_address = models.TextField(
        max_length=150,
        verbose_name=_('Account owner address')
    )

    @property
    def end_date(self):
        return self.start_date + timedelta(days=3)

    def __str__(self):
        return f'Zosia {self.start_date.year}'

    def user_registration_start(self, user):
        if user.is_authenticated:
            return self.early_registration_start \
                if self.early_registration_start is not None \
                   and user.person_type == UserInternals.PERSON_EARLY_REGISTERING \
                else self.registration_start

        return self.registration_start

    def is_user_registration_open(self, user):
        if self.user_registration_start(user) > now():
            return False

        if self.registration_suspended:
            return user.is_authenticated \
                and user.person_type == UserInternals.PERSON_EARLY_REGISTERING

        return True

    @property
    def is_registration_over(self):
        return self.registration_end < now()

    @property
    def is_rooming_open(self):
        return self.rooming_start - timedelta(minutes=MAX_BONUS_MINUTES) <= now()

    @property
    def is_rooming_over(self):
        return self.rooming_end < now()

    @property
    def is_lectures_open(self):
        return self.lecture_registration_start <= now() <= self.lecture_registration_end

    def can_user_choose_room(self, user_prefs, time=None):
        return self.get_rooming_status(user_prefs, time) == RoomingStatus.ROOMING_PROGRESS

    def get_rooming_status(self, user_prefs, time=None):
        if time is None:
            time = now()

        user_start_time = user_prefs.rooming_start_time

        if user_start_time is None:
            return RoomingStatus.ROOMING_UNAVAILABLE

        if time < user_start_time:
            return RoomingStatus.BEFORE_ROOMING

        if time > self.rooming_end:
            return RoomingStatus.AFTER_ROOMING

        return RoomingStatus.ROOMING_PROGRESS

    def validate_unique(self, **kwargs):
        # NOTE: If this instance is not yet saved, self.pk == None
        # So this query will take all active objects from db
        if self.active and Zosia.objects.exclude(pk=self.pk).filter(active=True).exists():
            raise ValidationError(_('Only one Zosia may be active at any given time'))

        super(Zosia, self).validate_unique(**kwargs)


    def get_discount_for_round(self, round):
        if round <= 0 or round > 3:
            return 0

        if round == 1:
            return self.first_discount
        if round == 2:
            return self.second_discount
        return self.third_discount


    def clean(self):
        if self.early_registration_start is not None:
            if self.early_registration_start > self.registration_start:
                raise ValidationError({
                    "early_registration_start": ValidationError(
                        _("Early registration opening time cannot be after general registration "
                          "opening time")
                    )
                })


class BusManager(models.Manager):
    def find_with_free_places(self, zosia):
        return self \
            .filter(zosia=zosia) \
            .annotate(passengers_num=Count('passengers')) \
            .filter(capacity__gt=F('passengers_num'))

    def find_available(self, zosia, passenger=None):
        query = Q(capacity__gt=F('passengers_num'))

        if passenger is not None:
            query = query | Q(passengers=passenger)

        return self \
            .filter(zosia=zosia) \
            .annotate(passengers_num=Count('passengers')) \
            .filter(query) \
            .distinct()


class Bus(models.Model):
    class Meta:
        verbose_name_plural = 'Buses'

    objects = BusManager()

    zosia = models.ForeignKey(Zosia, related_name='buses', on_delete=models.CASCADE)
    capacity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(500)])
    departure_time = models.DateTimeField()
    name = models.TextField(default="Bus")

    def __str__(self):
        return f'{self.name} {format_in_zone(self.departure_time, "Europe/Warsaw", "(%H:%M %Z)")}'

    @property
    def free_seats(self):
        return self.capacity - self.passengers_count

    @property
    def passengers_count(self):
        return self.passengers.count()

    @property
    def paid_passengers_count(self):
        return self.passengers.filter(payment_accepted=True).count()

    def passengers_to_string(self, paid=False, student=None):
        bus_passengers = self.passengers.order_by("user__last_name", "user__first_name")

        if paid:
            bus_passengers = bus_passengers.filter(payment_accepted=True)

        if student is not None:
            if student:
                bus_passengers = bus_passengers.filter(is_student=True)
            else:
                bus_passengers = bus_passengers.filter(is_student=False)

        return DELIMITER.join(map(lambda p: str(p.user), bus_passengers))
