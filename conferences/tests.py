import os
from datetime import datetime, timedelta, time

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.shortcuts import reverse
from django.contrib.auth import get_user_model

from users.models import Organization
from .models import Zosia, Place, UserPreferences, Bus
from .forms import UserPreferencesForm
from .test_helpers import new_zosia, new_user, new_bus, PRICE_ACCOMODATION, PRICE_BASE, \
    PRICE_BONUS, PRICE_BREAKFAST, PRICE_DINNER, PRICE_TRANSPORT


User = get_user_model()


class ZosiaTestCase(TestCase):
    def setUp(self):
        new_zosia()
        self.active = new_zosia(active=True)
        new_zosia()

    def test_only_one_active_Zosia_can_exist(self):
        """Creating another active Zosia throws an error"""
        with self.assertRaises(ValidationError):
            new_zosia(active=True, commit=False).full_clean()

    def test_find_active(self):
        """Zosia.find_active returns active Zosia"""
        self.assertEqual(self.active.pk, Zosia.objects.find_active().pk)

    def test_end_date(self):
        """Zosia has 4 days"""
        self.assertEqual(self.active.end_date, self.active.start_date + timedelta(3))


class BusTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.normal = new_user(0)
        self.normal2 = new_user(1)
        self.zosia = new_zosia()

        self.bus1 = new_bus(zosia=self.zosia, capacity=0)
        self.bus2 = new_bus(zosia=self.zosia, capacity=1)
        self.bus3 = new_bus(zosia=self.zosia, capacity=2)

    def test_find_buses_with_free_places(self):
        buses = Bus.objects.find_with_free_places(self.zosia)
        self.assertEqual(buses.count(), 2)

        UserPreferences.objects.create(
            user=self.normal,
            bus=self.bus2,
            zosia=self.zosia
        )
        buses = Bus.objects.find_with_free_places(self.zosia)
        self.assertEqual(buses.count(), 1)


class UserPreferencesTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.normal = new_user(0)
        self.zosia = new_zosia()

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

        self.assertEqual(user_prefs.price, PRICE_BASE)

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

        self.assertEqual(user_prefs.price,
                         PRICE_BASE + PRICE_BONUS)

    def test_price_partial_day(self):
        user_prefs = self.makeUserPrefs(
            accomodation_day_1=True,
            dinner_1=True,
            breakfast_2=False,
            accomodation_day_2=False,
            dinner_2=False,
            breakfast_3=False,
            accomodation_day_3=False,
            dinner_3=False,
            breakfast_4=False,
        )

        self.assertEqual(user_prefs.price,
                         PRICE_BASE + PRICE_DINNER)


class UserPreferencesFormTestCase(TestCase):
    def setUp(self):
        pass

    def makeUserPrefsForm(self, **override):
        defaults = {
            'contact': 'fb: me',
            'shirt_size': 'S',
            'shirt_type': 'f',
        }
        defaults.update(**override)
        return UserPreferencesForm(defaults)

    def test_basic_form(self):
        self.assertTrue(self.makeUserPrefsForm().is_valid())

    def test_accomodation_must_be_chosen_for_dinner_or_breakfast(self):
        form = self.makeUserPrefsForm(breakfast_2=True, accomodation_2=False)
        self.assertFalse(form.is_valid())

    def test_bus_choices_with_user(self):
        # TODO
        pass


class RegisterViewTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.normal = new_user(0)
        self.zosia = new_zosia()
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

    def test_user_cannot_change_accomodation_after_paid(self):
        UserPreferences.objects.create(user=self.normal,
                                       zosia=self.zosia,
                                       accomodation_day_1=False,
                                       payment_accepted=True)
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 1)
        self.client.login(username="john", password="johnpassword")
        response = self.client.post(self.url,
                                    data={
                                        'accomodation_day_1': True,
                                        'shirt_size': 'M',
                                        'shirt_type': 'f',
                                        'contact': 'fb: me',
                                    },
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        prefs = UserPreferences.objects.filter(user=self.normal).first()
        self.assertFalse(prefs.accomodation_day_1)
        # Sanity check ;)
        self.assertEqual(prefs.shirt_size, 'M')
