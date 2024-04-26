# -*- coding: utf-8 -*-

from conferences.models import Place, Transport, Zosia
from users.models import Organization, User, UserPreferences
from utils.constants import UserInternals
from utils.time_manager import now, timedelta_since_now

# NOTE: Using powers of 2 makes it easier to test if sums are precise
PRICE_ACCOMMODATION = 1 << 1
PRICE_BREAKFAST = 1 << 2
PRICE_DINNER = 1 << 3
PRICE_BASE = 1 << 4
PRICE_TRANSPORT = 1 << 5
PRICE_FULL = 1 << 6

USER_DATA = [
    ('mccartney@thebeatles.com', 'paul!password'),
    ('lennon@thebeatles.com', 'john!password'),
    ('harrison@thebeatles.com', 'george!password'),
    ('starr@thebeatles.com', 'ringo!password')
]


def login_as_user(user, client, /):
    return client.login(
        email=user.email,
        password=next(filter(lambda x: x[0] == user.email, USER_DATA))[1]
    )


def create_zosia(**kwargs):
    time = now()
    place = Place.objects.create(
        name='Mieszko',
        address='FooBar@Katowice',
        town='Katowice'
    )
    defaults = {
        'active': False,
        'start_date': time,
        'place': place,
        'early_registration_start': None,
        'registration_start': time,
        'registration_end': timedelta_since_now(minutes=10),
        'rooming_start': timedelta_since_now(days=-1),
        'rooming_end': timedelta_since_now(days=1),
        'lecture_registration_start': time,
        'lecture_registration_end': timedelta_since_now(minutes=10),
        'price_accommodation': PRICE_ACCOMMODATION,
        'price_accommodation_breakfast': PRICE_BREAKFAST,
        'price_accommodation_dinner': PRICE_DINNER,
        'price_whole_day': PRICE_FULL,
        'price_base': PRICE_BASE,
        'price_transport': PRICE_TRANSPORT,
        'account_number': 'PL59 1090 2402 4156 9594 3379 3484',
        'account_owner': 'Joan Doe',
        'account_bank': 'SuperBank',
        'account_address': 'ul. Fajna 42, 51-109, Wrocław'
    }
    defaults.update(kwargs)
    return Zosia.objects.create(**defaults)


def create_user(index, /, person_type=UserInternals.PERSON_NORMAL, **kwargs):
    first_name = USER_DATA[index][1].split("!", 1)[0]
    last_name = USER_DATA[index][0].split("@", 1)[0]

    return User.objects.create_user(email=USER_DATA[index][0], password=USER_DATA[index][1],
                                    first_name=first_name, last_name=last_name,
                                    person_type=person_type, **kwargs)


def create_user_preferences(user, zosia, **kwargs):
    return UserPreferences.objects.create(user=user, zosia=zosia, terms_accepted=True, **kwargs)


def create_organization(name, user=None, **kwargs):
    return Organization.objects.create(name=name, user=user, **kwargs)


def create_transport(zosia, **kwargs):
    defaults = {
        'capacity': 0,
        'departure_time': now(),
    }
    defaults.update(kwargs)
    return Transport.objects.create(zosia=zosia, **defaults)
