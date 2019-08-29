from datetime import timedelta
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import lorem_ipsum

from conferences.models import Bus, Place, Zosia
from lectures.models import Lecture
from questions.models import QA
from rooms.models import Room
from utils.time_manager import TimeManager

User = get_user_model()


def create_question():
    data = {
        'question': lorem_ipsum.sentence()[:100],
        'answer': ''.join(lorem_ipsum.paragraphs(2))[:400]
    }
    return QA.objects.create(**data)


def create_lecture(zosia, author):
    data = {
        'zosia': zosia,
        'info': lorem_ipsum.words(60)[:750],
        'title': lorem_ipsum.sentence()[:255],
        'abstract': ' '.join(lorem_ipsum.paragraphs(3))[:1000],
        'duration': '15',
        'lecture_type': random.randint(0, 2),
        'person_type': '2',
        'description': lorem_ipsum.words(20)[:255],
        'author': author
    }
    return Lecture.objects.create(**data)


def random_date_before(date, range_days):
    return TimeManager.to_timezone(date - timedelta(days=random.randint(1, range_days)))


def create_place():
    data = {
        'name': 'Old Forest Inn',
        'url': 'http://google.com',
        'address': 'Bakery Street 23, Glasgow'}
    return Place.objects.create(**data)


def create_buses(zosia):
    Bus.objects.create(zosia=zosia, time=TimeManager.today_time(hour=16), capacity=45)
    Bus.objects.create(zosia=zosia, time=TimeManager.today_time(hour=18), capacity=45)


def create_active_zosia(place, **kwargs):
    today = TimeManager.now()
    start_date = TimeManager.timedelta_from_now(days=350)
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
    start_date = random_date_before(TimeManager.now(), 400)
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
        'price_accomodation': 50,
        'price_accomodation_breakfast': 10,
        'price_accomodation_dinner': 15,
        'price_whole_day': 70,
        'price_transport': 50,
        'account_number': 36023320000000008,
        'account_details': 'Joan Doe, Bag End 666, Shire'
    }
    data.update(kwargs)
    zosia = Zosia.objects.create(**data)
    create_buses(zosia)
    return zosia


def create_admin_user():
    data = {
        'email': 'zosia@example.com',
        'first_name': 'ZOSIA',
        'last_name': 'KSIOWA',
    }
    u = User.objects.get_or_create(**data)[0]
    u.set_password('admin')
    u.save()
    return u


def create_room(zosia):
    data = {
        'name': lorem_ipsum.words(1),
        'description': lorem_ipsum.words(3),
        'capacity': random.randint(1, 6),
        'zosia': zosia,
    }
    return Room.objects.create(**data)


class Command(BaseCommand):
    help = 'Create custom data in database'

    def handle(self, *args, **kwargs):
        place = create_place()
        self.stdout.write('Place for zosia has been created!')

        zosia = create_active_zosia(place)
        self.stdout.write('Active zosia has been created!')

        for i in range(2):
            create_past_zosia(place)
            self.stdout.write('Past zosia #%d has been created' % i)

        admin = create_admin_user()
        self.stdout.write('Admin user has been created')

        for i in range(4):
            create_lecture(zosia, admin)
            self.stdout.write('Created lecture #%d' % i)

        question_num = random.randint(3, 13)
        for i in range(question_num):
            create_question()
            self.stdout.write('Created question #%d' % i)

        room_num = random.randint(7, 20)
        for i in range(room_num):
            create_room(zosia)
            self.stdout.write('Created room #%d' % i)

        self.stdout.write(
            self.style.SUCCESS('Database has been filled with some data!'))
