import random

from django.core.management.base import BaseCommand
from django.utils import lorem_ipsum

from conferences.models import Bus, Place, Zosia
from lectures.models import Lecture
from questions.models import QA
from blog.models import BlogPost
from rooms.models import Room
from users.models import User, Organization, UserPreferences
from utils.constants import FULL_DURATION_CHOICES, LECTURE_TYPE, LectureInternals, MAX_BONUS_MINUTES
from utils.time_manager import now, time_point, timedelta_since, timedelta_since_now


IMIONA = ['Zosia', 'Kasia', 'Basia', 'Ula', 'Natalia', 'Ania', 'Ewa', 'Alicja']


def create_question():
    data = {
        'question': lorem_ipsum.words(random.randint(5, 10)) + "?",
        'answer': ''.join(lorem_ipsum.paragraphs(1))[:400],
    }
    return QA.objects.create(**data)


def create_lecture(zosia, author):
    data = {
        'zosia': zosia,
        'requests': lorem_ipsum.words(60)[:750],
        'events': lorem_ipsum.words(60)[:750],
        'title': lorem_ipsum.sentence()[:255],
        'abstract': ' '.join(lorem_ipsum.paragraphs(3))[:1000],
        'duration': random.choice(FULL_DURATION_CHOICES)[0],
        'lecture_type': random.choice(LECTURE_TYPE)[0],
        'person_type': LectureInternals.PERSON_NORMAL,
        'description': lorem_ipsum.words(random.randint(10, 20))[:255],
        'author': author,
        'accepted': random_bool(),
    }
    return Lecture.objects.create(**data)


def create_blogpost(author):
    data = {
        'title': lorem_ipsum.words(random.randint(5, 10)),
        'content': ''.join(lorem_ipsum.words(random.randint(10, 30)))[:500],
        'publication': now(),
        'author': author,
    }
    return BlogPost.objects.create(**data)


def random_date_before(date, range_days):
    return timedelta_since(date, days=-random.randint(1, range_days))


def create_place():
    data = {
        'name': 'Old Forest Inn',
        'url': 'http://google.com',
        'address': 'Bakery Street 23, Glasgow'
    }
    return Place.objects.create(**data)


def create_buses(zosia):
    time = now()

    Bus.objects.create(
        zosia=zosia,
        departure_time=time_point(time.year, time.month, time.day, 16),
        capacity=45
    )

    Bus.objects.create(
        zosia=zosia,
        departure_time=time_point(time.year, time.month, time.day, 18),
        capacity=45
    )


def create_active_zosia(place, **kwargs):
    today = now()
    start_date = timedelta_since_now(days=350)
    start = today
    end = start_date
    data = {
        'active': True,
        'place': place,
        'registration_start': start,
        'registration_end': end,
        'start_date': start_date,
        'rooming_start': start,
        'rooming_end': end,
        'lecture_registration_start': start,
        'lecture_registration_end': end,
    }
    return create_zosia(**data)


def create_past_zosia(place, **kwargs):
    start_date = random_date_before(now(), 400)
    registration_end = random_date_before(start_date, 20)
    registration_start = random_date_before(registration_end, 40)
    rooming_end = registration_end
    rooming_start = random_date_before(rooming_end, 12)
    data = {
        'place': place,
        'registration_start': registration_start,
        'registration_end': registration_end,
        'start_date': start_date,
        'rooming_start': rooming_start,
        'rooming_end': rooming_end,
        'lecture_registration_start': rooming_start,
        'lecture_registration_end': rooming_end,
    }
    return create_zosia(**data)


def create_zosia(**kwargs):
    data = {
        'description': 'Once upon a time there were apes',
        'price_accommodation': 50,
        'price_accommodation_breakfast': 60,
        'price_accommodation_dinner': 65,
        'price_whole_day': 70,
        'price_transport': 50,
        'account_number': 'PL59 1090 2402 4156 9594 3379 3484',
        'account_owner': 'Joan Doe',
        'account_bank': 'SuperBank',
        'account_address': 'ul. Fajna 42, 51-109, Wrocław'
    }
    data.update(kwargs)
    zosia = Zosia.objects.create(**data)
    create_buses(zosia)
    return zosia


def create_sample_staff_user():
    data = {
        'email': 'zosia@example.com',
        'first_name': 'Zosia',
        'last_name': 'Ksiowa',
        'password': 'pass',
        'is_staff': True
    }

    return User.objects.create_user(**data)


def random_bool():
    return random.random() < 0.5


def create_random_user_with_preferences(zosia, id):
    data = {
        'email': f'zosia{id}@example.com',
        'first_name': random.choice(IMIONA),
        'last_name': f'Testowa{id}',
    }
    u = User.objects.get_or_create(**data)[0]
    u.set_password('pass')
    u.save()

    org = Organization.objects.create(name=f"org_{id}", user=u, accepted=random_bool()) \
        if random_bool() else None

    accommodation_day_1 = random_bool()
    dinner_day_1 = random_bool() if accommodation_day_1 else False
    breakfast_day_2 = random_bool() if accommodation_day_1 else False

    accommodation_day_2 = random_bool()
    dinner_day_2 = random_bool() if accommodation_day_2 else False
    breakfast_day_3 = random_bool() if accommodation_day_2 else False

    accommodation_day_3 = random_bool()
    dinner_day_3 = random_bool() if accommodation_day_3 else False
    breakfast_day_4 = random_bool() if accommodation_day_3 else False

    phone_number = f'+48 {random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}'
    bus = random.choice(Bus.objects.find_with_free_places(zosia)) if random_bool() else None

    payment_acc = random_bool()
    bonus = random.randint(1, MAX_BONUS_MINUTES) if payment_acc else 0

    UserPreferences.objects.create(
        user=u,
        zosia=zosia,
        organization=org,
        bus=bus,
        accommodation_day_1=accommodation_day_1,
        dinner_day_1=dinner_day_1,
        accommodation_day_2=accommodation_day_2,
        breakfast_day_2=breakfast_day_2,
        dinner_day_2=dinner_day_2,
        accommodation_day_3=accommodation_day_3,
        breakfast_day_3=breakfast_day_3,
        dinner_day_3=dinner_day_3,
        breakfast_day_4=breakfast_day_4,
        contact=phone_number,
        payment_accepted=payment_acc,
        bonus_minutes=bonus,
        terms_accepted=True,
    )
    return u


def create_room(number):
    if random.random() < 0.1:
        data = {
            'name': f"Nr. {number}",
            'description': lorem_ipsum.words(random.randint(3, 6)),
            'beds_double': 1,
            'available_beds_double': 1,
        }
    else:
        bed_single = random.randint(2, 6)
        data = {
            'name': f"Nr. {number}",
            'description': lorem_ipsum.words(random.randint(3, 6)),
            'beds_single': bed_single,
            'available_beds_single': random.randint(2, bed_single),
        }
    return Room.objects.create(**data)


class Command(BaseCommand):
    help = 'Create custom data in database'

    def handle(self, *args, **kwargs):
        if Zosia.objects.filter(active=True).count() > 0:
            self.stdout.write('\033[1;91mThere is already active Zosia in database.'
                              '\033[0m Do you want to create data anyway? [y/n]')
            choice = input().lower()
            if choice not in {'yes', 'y'}:
                return

        place = create_place()
        self.stdout.write('Place for zosia has been created!')

        zosia = create_active_zosia(place)
        self.stdout.write('Active zosia has been created!')

        # for i in range(2):
        #     create_past_zosia(place)
        #     self.stdout.write('Past zosia #%d has been created' % i)

        all_users = []

        sample_staff_user = create_sample_staff_user()
        self.stdout.write('Sample user has been created')
        all_users.append(sample_staff_user)

        for i in range(5):
            user_with_prefs = create_random_user_with_preferences(zosia, i + 1)
            self.stdout.write(f"Created random user #{i}")
            all_users.append(user_with_prefs)

        for i in range(4):
            author = random.choice(all_users)
            create_lecture(zosia, author)
            self.stdout.write(f"Created lecture #{i}")

        create_blogpost(sample_staff_user)

        question_num = random.randint(3, 9)
        for i in range(question_num):
            create_question()
            self.stdout.write(f"Created question #{i}")

        room_num = random.randint(7, 20)
        for i in range(1, room_num + 1):
            create_room(i)
            self.stdout.write(f"Created room #{i}")

        self.stdout.write(
            self.style.SUCCESS('Database has been filled with some data!'))
