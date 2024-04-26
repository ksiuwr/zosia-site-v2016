from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.utils import IntegrityError
from django.forms import ValidationError
from django.shortcuts import reverse
from django.test import TestCase

from lectures.forms import LectureAdminForm, LectureForm
from lectures.models import Lecture
from utils.constants import LECTURE_NORMAL_MAX_DURATION, LECTURE_SPONSOR_MAX_DURATION, \
    LectureInternals, UserInternals, WORKSHOP_MIN_DURATION
from utils.test_helpers import create_user, create_zosia, login_as_user
from utils.time_manager import now, timedelta_since_now

User = get_user_model()


class LectureTestCase(TestCase):
    def setUp(self):
        time = now()
        self.zosia = create_zosia(
            start_date=timedelta_since_now(days=1),
            active=True,
            price_accommodation=23,
            registration_end=time,
            registration_start=time,
            rooming_start=time,
            rooming_end=time,
            price_transport=0,
            lecture_registration_start=time,
            lecture_registration_end=time,
            price_accommodation_dinner=0,
            price_accommodation_breakfast=0,
            price_whole_day=0
        )
        self.normal_user = create_user(0, UserInternals.PERSON_NORMAL)
        self.sponsor_user = create_user(1, UserInternals.PERSON_SPONSOR)


class ModelTestCase(LectureTestCase):
    def test_lecture_is_invalid_without_zosia(self):
        lecture = Lecture(
            title="foo",
            abstract="foo",
            duration=10,
            lecture_type=LectureInternals.TYPE_LECTURE,
            author=self.normal_user
        )

        with self.assertRaises(ValidationError):
            lecture.full_clean()

    def test_lecture_is_invalid_without_title(self):
        lecture = Lecture(
            zosia=self.zosia,
            abstract="foo",
            duration=10,
            lecture_type=LectureInternals.TYPE_LECTURE,
            author=self.normal_user
        )

        with self.assertRaises(ValidationError):
            lecture.full_clean()

    def test_lecture_is_invalid_without_abstract(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            duration=10,
            lecture_type=LectureInternals.TYPE_LECTURE,
            author=self.normal_user
        )

        with self.assertRaises(ValidationError):
            lecture.full_clean()

    def test_lecture_is_invalid_without_duration(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            abstract="foo",
            lecture_type=LectureInternals.TYPE_LECTURE,
            author=self.normal_user
        )

        with self.assertRaises(ValidationError):
            lecture.full_clean()

    def test_lecture_is_invalid_without_lecture_type(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            abstract="foo",
            duration=10,
            author=self.normal_user
        )

        with self.assertRaises(ValidationError):
            lecture.full_clean()

    def test_lecture_is_invalid_without_author(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            abstract="foo",
            duration=10,
            lecture_type=LectureInternals.TYPE_LECTURE
        )

        with self.assertRaises(ValidationError):
            lecture.full_clean()

    def test_lecture_is_invalid_for_normal_person_with_duration_more_than_60(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            abstract="bar",
            duration=75,
            lecture_type=LectureInternals.TYPE_LECTURE,
            author=self.normal_user
        )

        with self.assertRaises(ValidationError):
            lecture.full_clean()

    def test_lecture_is_valid_for_sponsor_person_with_duration_more_than_60(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            abstract="bar",
            duration=75,
            lecture_type=LectureInternals.TYPE_LECTURE,
            author=self.sponsor_user
        )

        count = Lecture.objects.count()

        try:
            lecture.full_clean()
        except ValidationError as e:
            self.fail("Full clean failed! {}".format(e.message_dict))

        lecture.save()
        self.assertEqual(count + 1, Lecture.objects.count())

    def test_lecture_is_valid_for_normal_person(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            abstract="bar",
            duration=20,
            lecture_type=LectureInternals.TYPE_LECTURE,
            author=self.normal_user
        )

        count = Lecture.objects.count()

        try:
            lecture.full_clean()
        except ValidationError as e:
            self.fail("Full clean failed! {}".format(e.message_dict))

        lecture.save()
        self.assertEqual(count + 1, Lecture.objects.count())

    def test_lecture_is_valid_with_maximal_duration_for_normal_person(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            abstract="bar",
            duration=LECTURE_NORMAL_MAX_DURATION,
            lecture_type=LectureInternals.TYPE_LECTURE,
            author=self.normal_user
        )

        count = Lecture.objects.count()

        try:
            lecture.full_clean()
        except ValidationError as e:
            self.fail("Full clean failed! {}".format(e.message_dict))

        lecture.save()
        self.assertEqual(count + 1, Lecture.objects.count())

    def test_lecture_is_valid_for_sponsor_person_with_maximal_duration(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            abstract="bar",
            duration=LECTURE_SPONSOR_MAX_DURATION,
            lecture_type=LectureInternals.TYPE_LECTURE,
            author=self.sponsor_user
        )

        count = Lecture.objects.count()

        try:
            lecture.full_clean()
        except ValidationError as e:
            self.fail("Full clean failed! {}".format(e.message_dict))

        lecture.save()
        self.assertEqual(count + 1, Lecture.objects.count())

    def test_workshop_is_invalid_with_duration_less_than_30(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            abstract="bar",
            duration=15,
            lecture_type=LectureInternals.TYPE_WORKSHOP,
            author=self.normal_user
        )

        with self.assertRaises(ValidationError):
            lecture.full_clean()

    def test_workshop_is_valid(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            abstract="bar",
            duration=75,
            lecture_type=LectureInternals.TYPE_WORKSHOP,
            author=self.sponsor_user
        )

        count = Lecture.objects.count()

        try:
            lecture.full_clean()
        except ValidationError as e:
            self.fail("Full clean failed! {}".format(e.message_dict))

        lecture.save()
        self.assertEqual(count + 1, Lecture.objects.count())

    def test_workshop_is_valid_with_minimal_duration(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            abstract="bar",
            duration=WORKSHOP_MIN_DURATION,
            lecture_type=LectureInternals.TYPE_WORKSHOP,
            author=self.normal_user
        )

        count = Lecture.objects.count()

        try:
            lecture.full_clean()
        except ValidationError as e:
            self.fail("Full clean failed! {}".format(e.message_dict))

        lecture.save()
        self.assertEqual(count + 1, Lecture.objects.count())

    def test_workshop_is_valid_with_maximal_duration(self):
        lecture = Lecture(
            zosia=self.zosia,
            title="foo",
            abstract="bar",
            duration=120,
            lecture_type=LectureInternals.TYPE_WORKSHOP,
            author=self.normal_user
        )

        count = Lecture.objects.count()

        try:
            lecture.full_clean()
        except ValidationError as e:
            self.fail("Full clean failed! {}".format(e.message_dict))

        lecture.save()
        self.assertEqual(count + 1, Lecture.objects.count())

    def test_str(self):
        title = "foo bar baz"
        lecture = Lecture.objects.create(
            zosia=self.zosia,
            title=title,
            abstract="qux quux quuux",
            duration=15,
            lecture_type=LectureInternals.TYPE_LECTURE,
            author=self.normal_user
        )
        lecture.supporting_authors.add(self.sponsor_user)

        self.assertEqual(str(lecture), f"{self.normal_user}, {self.sponsor_user} - {title}")

    def test_toggle_accepted(self):
        lecture = Lecture.objects.create(
            zosia=self.zosia,
            title="foo",
            abstract="bar",
            duration=45,
            lecture_type=LectureInternals.TYPE_LECTURE,
            author=self.normal_user
        )

        self.assertFalse(lecture.accepted)

        lecture.toggle_accepted()

        self.assertTrue(lecture.accepted)


class FormTestCase(LectureTestCase):
    def test_user_form_no_data(self):
        form = LectureForm({})
        self.assertFalse(form.is_valid())

    def test_user_create_object(self):
        form = LectureForm({'title': 'foo', 'abstract': 'bar', 'duration': 45,
                            'lecture_type': LectureInternals.TYPE_LECTURE})

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                form.save()

        count = Lecture.objects.count()
        obj = form.save(commit=False)
        obj.zosia = self.zosia
        obj.author = self.normal_user
        obj.save()
        self.assertEqual(count + 1, Lecture.objects.count())

    def test_admin_form_no_data(self):
        form = LectureAdminForm({})
        self.assertFalse(form.is_valid())

    def test_admin_create_object(self):
        form = LectureAdminForm({'title': 'foo', 'abstract': 'bar', 'duration': 45,
                                 'lecture_type': LectureInternals.TYPE_LECTURE,
                                 'author': self.normal_user.id})

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
        self.superuser = create_user(3, is_staff=True)

    def test_index_get(self):
        response = self.client.get(reverse('lectures_index'), follow=True)
        self.assertEqual(response.status_code, 200)
        lectures = Lecture.objects.filter(zosia=self.zosia, accepted=True)
        self.assertEqual(set(response.context['objects']), set(lectures))
        self.assertTemplateUsed('lectures/index.html')

    def test_display_all_no_user(self):
        response = self.client.get(reverse('lectures_all_staff'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/lectures/all')

    def test_display_all_normal(self):
        login_as_user(self.normal_user, self.client)
        response = self.client.get(reverse('lectures_all_staff'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/lectures/all')

    def test_display_all_staff(self):
        login_as_user(self.superuser, self.client)
        response = self.client.get(reverse('lectures_all_staff'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('lectures/all.html')
