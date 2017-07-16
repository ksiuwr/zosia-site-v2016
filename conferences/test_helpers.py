from datetime import datetime, time, timedelta

from users.models import User

from .models import Bus, Place, UserPreferences, Zosia

# NOTE: Using powers of 2 makes it easier to test if sums are precise
PRICE_ACCOMODATION = 1 << 1
PRICE_BREAKFAST = 1 << 2
PRICE_DINNER = 1 << 3
PRICE_BASE = 1 << 4
PRICE_TRANSPORT = 1 << 5
PRICE_BONUS = 1 << 6


def new_zosia(commit=True, **kwargs):
    now = datetime.now()
    place, _ = Place.objects.get_or_create(
        name='Mieszko',
        address='FooBar@Katowice'
    )
    defaults = {
        'active': False,
        'start_date': now,
        'place': place,
        'registration_start': now,
        'registration_end': now,
        'rooming_start': now,
        'rooming_end': now,
        'lecture_registration_start': now,
        'lecture_registration_end': now,
        'price_accomodation': PRICE_ACCOMODATION,
        'price_accomodation_breakfast': PRICE_BREAKFAST,
        'price_accomodation_dinner': PRICE_DINNER,
        'price_whole_day': PRICE_BONUS,
        'price_base': PRICE_BASE,
        'price_transport': PRICE_TRANSPORT,
        'account_number': '',
    }
    defaults.update(kwargs)
    zosia = Zosia(**defaults)
    if commit:
        zosia.save()
    return zosia


USER_DATA = [
    ['john', 'lennon@thebeatles.com', 'johnpassword'],
    ['ringo', 'starr@thebeatles.com', 'ringopassword']
]


def new_user(ind, **kwargs):
    return User.objects.create_user(*USER_DATA[ind], **kwargs)


def user_login(user):
    return {
        'username': user.username,
        'password': next(filter(lambda x: x[0] == user.username, USER_DATA))[2]
    }


def new_bus(commit=True, **override):
    zosia = override['zosia'] or new_zosia()
    defaults = {
        'capacity': 0,
        'time': time(1),
        'zosia': zosia,

    }
    defaults.update(**override)
    bus = Bus(**defaults)
    if commit:
        bus.save()
    return bus


def user_preferences(**kwargs):
    return UserPreferences.objects.create(**kwargs)
