from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.utils import IntegrityError
from django.forms import ValidationError
from django.shortcuts import reverse
from django.test import TestCase

from conferences.models import Place, Zosia
from lectures.forms import LectureAdminForm, LectureForm
from lectures.models import Lecture
from utils.time_manager import now_time, timedelta_since_now

User = get_user_model()


class LectureTestCase(TestCase):
    def setUp(self):
        now = now_time()
        place = Place.objects.create(name="Mieszko", address="foo")
        self.zosia = Zosia.objects.create(
            start_date=timedelta_since_now(days=1),
            active=True, place=place,
            price_accomodation=23,
            registration_end=now,
            registration_start=now,
            rooming_start=now,
            rooming_end=now,
            price_transport=0,
            lecture_registration_start=now,
            lecture_registration_end=now,
            price_accomodation_dinner=0,
            price_accomodation_breakfast=0,
            price_whole_day=0)
        self.user = User.objects.create_user('john@thebeatles.com',
                                             'johnpassword',
                                             first_name='john')


class ModelTestCase(LectureTestCase):
    def test_must_have_zosia(self):
        lecture = Lecture(
            title="foo",
            abstract="foo",
            duration="5",
            lecture_type="1",
            person_type="0",
            author=self.user)
        with self.assertRaises(ValidationError):
            lecture.full_clean()

    def test_must_have_title(self):
        lecture = Lecture(
            zosia=self.zosia,
            abstract="foo",
            duration="5",
            lecture_type="1",
            person_type="0",
            author=self.user)
        with self.assertRaises(ValidationError):
            lecture.full_clean()

    def test_must_have_abstract(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            duration="5",
            lecture_type="1",
            person_type="0",
            author=self.user)
        with self.assertRaises(ValidationError):
            lecture.full_clean()

    def test_must_have_duration(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            abstract="5",
            lecture_type="1",
            person_type="0",
            author=self.user)
        with self.assertRaises(ValidationError):
            lecture.full_clean()

    def test_must_have_lecture_type(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            duration="5",
            abstract="1",
            person_type="0",
            author=self.user)
        with self.assertRaises(ValidationError):
            lecture.full_clean()

    def test_must_have_person_type(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            duration="5",
            lecture_type="1",
            abstract="0",
            author=self.user)
        with self.assertRaises(ValidationError):
            lecture.full_clean()

    def test_must_have_author(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            duration="5",
            lecture_type="1",
            person_type="0",
            abstract="foo")
        with self.assertRaises(ValidationError):
            lecture.full_clean()

    def test_create(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            abstract="bar",
            duration="5",
            lecture_type="1",
            person_type="0",
            author=self.user)

        count = Lecture.objects.count()
        try:
            lecture.full_clean()
        except ValidationError:
            self.fail("Full clean fail!")
        lecture.save()
        self.assertEqual(count + 1, Lecture.objects.count())

    def test_str(self):
        lecture = Lecture.objects.create(
            zosia=self.zosia,
            title="foo",
            abstract="bar",
            duration="5",
            lecture_type="1",
            person_type="0",
            author=self.user)
        self.assertEqual(str(lecture), "john - foo")

    def test_toggle_accept(self):
        lecture = Lecture.objects.create(
            zosia=self.zosia,
            title="foo",
            abstract="bar",
            duration="5",
            lecture_type="1",
            person_type="0",
            author=self.user)
        self.assertFalse(lecture.accepted)
        lecture.toggle_accepted()
        self.assertTrue(lecture.accepted)


class FormTestCase(LectureTestCase):
    def test_user_form_no_data(self):
        form = LectureForm({})
        self.assertFalse(form.is_valid())

    def test_user_create_object(self):
        form = LectureForm({'title': 'foo', 'abstract': 'bar',
                            'duration': '5', 'lecture_type': '1',
                            'person_type': '0'})
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                form.save()
        count = Lecture.objects.count()
        obj = form.save(commit=False)
        obj.zosia = self.zosia
        obj.author = self.user
        obj.save()
        self.assertEqual(count + 1, Lecture.objects.count())

    def test_admin_form_no_data(self):
        form = LectureAdminForm({})
        self.assertFalse(form.is_valid())

    def test_admin_create_object(self):
        form = LectureAdminForm({'title': 'foo', 'abstract': 'bar',
                                 'duration': '5', 'lecture_type': '1',
                                 'person_type': '0', 'author': self.user.id})
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                form.save()
        count = Lecture.objects.count()
        obj = form.save(commit=False)
        obj.zosia = self.zosia
        obj.save()
        self.assertEqual(count + 1, Lecture.objects.count())


class ViewsTestCase(LectureTestCase):
    def setUp(self):
        super().setUp()
        self.superuser = User.objects.create_user('paul@thebeatles.com',
                                                  'paulpassword')

    def test_index_get(self):
        response = self.client.get(reverse('lectures_index'), follow=True)
        self.assertEqual(response.status_code, 200)
        lectures = Lecture.objects.filter(accepted=True).filter(zosia=self.zosia)
        self.assertEqual(set(response.context['objects']), set(lectures))
        self.assertTemplateUsed('lectures/index.html')

    def test_display_all_no_user(self):
        response = self.client.get(reverse('lectures_all_staff'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/lectures/all')

    def test_display_all_normal(self):
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.get(reverse('lectures_all_staff'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/lectures/all')

    def test_display_all_staff(self):
        self.client.login(email='paul@thebeatles.com', password='paulpassword')
        response = self.client.get(reverse('lectures_all_staff'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('lectures/all.html')
