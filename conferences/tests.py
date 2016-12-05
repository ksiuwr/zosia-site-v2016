import os
from datetime import datetime, timedelta

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.shortcuts import reverse
from django.contrib.auth import get_user_model

from users.models import Organization
from .models import Zosia, Place, UserPreferences
from .forms import UserPreferencesForm


User = get_user_model()


# NOTE: Using powers of 2 makes it easier to test if sums are precise
PRICE_BONUS = 1
PRICE_ACCOMODATION = 1 << 1
PRICE_BREAKFAST = 1 << 2
PRICE_DINNER = 1 << 3
PRICE_BASE = 1 << 4
PRICE_TRANSPORT = 1 << 5


def new_zosia(**kwargs):
    now = datetime.now() + timedelta(1)
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
        'price_accomodation': PRICE_ACCOMODATION,
        'price_breakfast': PRICE_BREAKFAST,
        'price_dinner': PRICE_DINNER,
        'price_bonus_for_whole_day': PRICE_BONUS,
        'price_base': PRICE_BASE,
        'price_transport': PRICE_TRANSPORT,
        'account_number': '',
    }
    defaults.update(kwargs)
    return Zosia(**defaults)


class ZosiaTestCase(TestCase):
    def setUp(self):
        new_zosia().save()
        self.active = new_zosia(active=True)
        self.active.save()
        new_zosia().save()

    def test_only_one_active_Zosia_can_exist(self):
        """Creating another active Zosia throws an error"""
        with self.assertRaises(ValidationError):
            new_zosia(active=True).full_clean()

    def test_find_active(self):
        """Zosia.find_active returns active Zosia"""
        self.assertEqual(self.active.pk, Zosia.objects.find_active().pk)

    def test_end_date(self):
        """Zosia has 4 days"""
        self.assertEqual(self.active.end_date, self.active.start_date + timedelta(3))


class UserPreferencesTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.normal = User.objects.create_user('john', 'lennon@thebeatles.com',
                                               'johnpassword')
        self.normal.save()

        self.zosia = new_zosia()
        self.zosia.save()

    def makeUserPrefs(self, **override):
        defaults = {
            'user': self.normal,
            'zosia': self.zosia,
            'contact': 'fb: me',
            'shirt_size': 'S',
            'shirt_type': 'f',
        }
        defaults.update(**override)
        return UserPreferences(**defaults)

    def test_price_base(self):
        user_prefs = self.makeUserPrefs(
            accomodation_day_1=False,
            dinner_1=False,
            breakfast_2=False,
            accomodation_day_2=False,
            dinner_2=False,
            breakfast_3=False,
            accomodation_day_3=False,
            dinner_3=False,
            breakfast_4=False,
        )

        self.assertEqual(user_prefs.price(), PRICE_BASE)

    def test_price_whole_day(self):
        user_prefs = self.makeUserPrefs(
            accomodation_day_1=True,
            dinner_1=True,
            breakfast_2=True,
            accomodation_day_2=False,
            dinner_2=False,
            breakfast_3=False,
            accomodation_day_3=False,
            dinner_3=False,
            breakfast_4=False,
        )

        self.assertEqual(user_prefs.price(),
                         PRICE_BASE + PRICE_DINNER + PRICE_BREAKFAST + PRICE_ACCOMODATION - PRICE_BONUS)

    def test_price_partial_day(self):
        user_prefs = self.makeUserPrefs(
            accomodation_day_1=False,
            dinner_1=True,
            breakfast_2=True,
            accomodation_day_2=False,
            dinner_2=False,
            breakfast_3=False,
            accomodation_day_3=False,
            dinner_3=False,
            breakfast_4=False,
        )

        self.assertEqual(user_prefs.price(),
                         PRICE_BASE + PRICE_DINNER + PRICE_BREAKFAST)


class RegisterViewTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.normal = User.objects.create_user('john', 'lennon@thebeatles.com',
                                               'johnpassword')
        self.normal.save()

        self.zosia = new_zosia()
        self.zosia.save()

        self.url = reverse('user_zosia_register', kwargs={'zosia_id': self.zosia.pk})

    def test_get_no_user(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/accounts/login/?next={}'.format(self.url))

    def test_get_regular_user_not_registered(self):
        self.client.login(username="john", password="johnpassword")
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

        context = response.context[-1]
        self.assertEqual(context['form'].__class__, UserPreferencesForm)
        self.assertFalse('object' in context)

    def test_get_regular_user_already_registered(self):
        self.client.login(username="john", password="johnpassword")
        org = Organization.objects.create(name='ksi', accepted=True)
        user_prefs = UserPreferences.objects.create(zosia=self.zosia,
                                                    user=self.normal,
                                                    organization=org)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

        context = response.context[-1]
        self.assertEqual(context['form'].__class__, UserPreferencesForm)
        self.assertEqual(context['object'], user_prefs)

    def test_post_user_not_registered_empty_data(self):
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 0)
        self.client.login(username="john", password="johnpassword")
        response = self.client.post(self.url,
                                    data={},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 0)

    def test_post_user_not_registered_with_data(self):
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 0)
        self.client.login(username="john", password="johnpassword")
        response = self.client.post(self.url,
                                    data={
                                        'contact': 'fb: me',
                                        'shirt_size': 'S',
                                        'shirt_type': 'f',
                                    },
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 1)

    def test_post_user_already_registered(self):
        UserPreferences.objects.create(user=self.normal, zosia=self.zosia)
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 1)
        self.client.login(username="john", password="johnpassword")
        response = self.client.post(self.url,
                                    data={
                                        'contact': 'fb: me',
                                        'shirt_size': 'S',
                                        'shirt_type': 'f',
                                    },
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 1)
