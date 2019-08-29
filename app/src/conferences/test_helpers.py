from conferences.models import Bus, Place, UserPreferences, Zosia
from users.models import User
from utils.time_manager import TimeManager

# NOTE: Using powers of 2 makes it easier to test if sums are precise
PRICE_ACCOMODATION = 1 << 1
PRICE_BREAKFAST = 1 << 2
PRICE_DINNER = 1 << 3
PRICE_BASE = 1 << 4
PRICE_TRANSPORT = 1 << 5
PRICE_BONUS = 1 << 6


def new_zosia(commit=True, **kwargs):
    now = TimeManager.now()
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
        'rooming_start': TimeManager.timedelta_from_now(days=-1),
        'rooming_end': TimeManager.timedelta_from_now(days=1),
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
    ['lennon@thebeatles.com', 'johnpassword'],
    ['starr@thebeatles.com', 'ringopassword'],
    ['mccartney@thebeatles.com', 'paulpassword'],
    ['harrison@thebeatles.com', 'georgepassword']
]


def new_user(ind, **kwargs):
    return User.objects.create_user(*USER_DATA[ind], **kwargs)


def user_login(user):
    return {
        'email': user.email,
        'password': next(filter(lambda x: x[0] == user.email, USER_DATA))[1]
    }


def new_bus(commit=True, **override):
    zosia = override['zosia'] or new_zosia()
    defaults = {
        'capacity': 0,
        'time': TimeManager.now(),
        'zosia': zosia,

    }
    defaults.update(**override)
    bus = Bus(**defaults)
    if commit:
        bus.save()
    return bus


def user_preferences(**kwargs):
    return UserPreferences.objects.create(**kwargs)
