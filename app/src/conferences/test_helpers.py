from conferences.models import Bus, Place, UserPreferences, Zosia
from users.models import User
from utils.time_manager import now, timedelta_since_now

# NOTE: Using powers of 2 makes it easier to test if sums are precise
PRICE_ACCOMODATION = 1 << 1
PRICE_BREAKFAST = 1 << 2
PRICE_DINNER = 1 << 3
PRICE_BASE = 1 << 4
PRICE_TRANSPORT = 1 << 5
PRICE_BONUS = 1 << 6


def create_zosia(commit=True, **kwargs):
    time = now()
    place, _ = Place.objects.get_or_create(
        name='Mieszko',
        address='FooBar@Katowice'
    )
    defaults = {
        'active': False,
        'start_date': time,
        'place': place,
        'registration_start': time,
        'registration_end': time,
        'rooming_start': timedelta_since_now(days=-1),
        'rooming_end': timedelta_since_now(days=1),
        'lecture_registration_start': time,
        'lecture_registration_end': time,
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


def create_user(index, **kwargs):
    return User.objects.create_user(*USER_DATA[index], **kwargs)


def user_login(user):
    return {
        'email': user.email,
        'password': next(filter(lambda x: x[0] == user.email, USER_DATA))[1]
    }


def create_bus(commit=True, **override):
    zosia = override['zosia'] or create_zosia()
    defaults = {
        'capacity': 0,
        'time': now(),
        'zosia': zosia,

    }
    defaults.update(**override)
    bus = Bus(**defaults)
    if commit:
        bus.save()
    return bus


def create_user_preferences(**kwargs):
    return UserPreferences.objects.create(**kwargs)
