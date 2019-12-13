from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import reverse
from django.test import TestCase

from conferences.models import Bus, Zosia
from conferences.test_helpers import create_bus, create_user, create_user_preferences, create_zosia
from users.forms import UserPreferencesForm
from users.models import Organization, UserPreferences
from utils.time_manager import now, time_point

User = get_user_model()


class ZosiaTestCase(TestCase):
    def setUp(self):
        create_zosia()
        self.active = create_zosia(active=True)
        create_zosia()

    def test_only_one_active_Zosia_can_exist(self):
        """Creating another active Zosia throws an error"""
        with self.assertRaises(ValidationError):
            create_zosia(active=True, commit=False).full_clean()

    def test_find_active(self):
        """Zosia.find_active returns active Zosia"""
        self.assertEqual(self.active.pk, Zosia.objects.find_active().pk)

    def test_end_date(self):
        """Zosia has 4 days"""
        self.assertEqual(self.active.end_date, self.active.start_date + timedelta(days=3))

    def test_can_user_choose_room_when_at_user_start_time(self):
        self.active.rooming_start = now()
        self.active.save()
        user_prefs = create_user_preferences(payment_accepted=True, bonus_minutes=0,
                                             user=create_user(0),
                                             zosia=self.active)

        result = self.active.can_user_choose_room(user_prefs)

        self.assertTrue(result)

    def test_can_user_choose_room_when_before_user_start_time(self):
        self.active.rooming_start = time_point(2016, 12, 23, 0, 0)
        self.active.save()
        user_prefs = create_user_preferences(payment_accepted=True, bonus_minutes=1,
                                             user=create_user(0),
                                             zosia=self.active)

        result = self.active.can_user_choose_room(user_prefs,
                                                  time=time_point(2016, 12, 22, 23, 58))
        self.assertFalse(result)

    def test_can_user_choose_room_when_after_user_start_time(self):
        self.active.rooming_start = time_point(2016, 12, 23, 0, 0)
        self.active.save()
        user_prefs = create_user_preferences(payment_accepted=True, bonus_minutes=3,
                                             user=create_user(0),
                                             zosia=self.active)

        result = self.active.can_user_choose_room(user_prefs,
                                                  time=time_point(2016, 12, 22, 23, 58))
        self.assertTrue(result)


class BusTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.normal = create_user(0)
        self.normal2 = create_user(1)
        self.zosia = create_zosia()

        self.bus1 = create_bus(zosia=self.zosia, capacity=0)
        self.bus2 = create_bus(zosia=self.zosia, capacity=1)
        self.bus3 = create_bus(zosia=self.zosia, capacity=2)

    def test_find_buses_with_free_places(self):
        buses = Bus.objects.find_with_free_places(self.zosia)
        self.assertEqual(buses.count(), 2)

        create_user_preferences(
            user=self.normal,
            bus=self.bus2,
            zosia=self.zosia
        )
        buses = Bus.objects.find_with_free_places(self.zosia)
        self.assertEqual(buses.count(), 1)


class RegisterViewTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.normal = create_user(0)
        self.zosia = create_zosia()
        self.url = reverse('user_zosia_register', kwargs={'zosia_id': self.zosia.pk})

    def test_get_no_user(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/accounts/login/?next={}'.format(self.url))

    def test_get_regular_user_not_registered(self):
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

        context = response.context[-1]
        self.assertEqual(context['form'].__class__, UserPreferencesForm)
        self.assertFalse('object' in context)

    def test_get_regular_user_already_registered(self):
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        org = Organization.objects.create(name='ksi', accepted=True)
        user_prefs = create_user_preferences(zosia=self.zosia,
                                             user=self.normal,
                                             organization=org)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

        context = response.context[-1]
        self.assertEqual(context['form'].__class__, UserPreferencesForm)
        self.assertEqual(context['object'], user_prefs)

    def test_post_user_not_registered_empty_data(self):
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 0)
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.post(self.url,
                                    data={},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 0)

    def test_post_user_not_registered_with_data(self):
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 0)
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.post(self.url,
                                    data={
                                        'contact': 'fb: me',
                                        'shirt_size': 'S',
                                        'shirt_type': 'f',
                                        'terms_accepted': True
                                    },
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 1)

    def test_post_user_already_registered(self):
        create_user_preferences(user=self.normal, zosia=self.zosia)
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 1)
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.post(self.url,
                                    data={
                                        'contact': 'fb: me',
                                        'shirt_size': 'S',
                                        'shirt_type': 'f',
                                        'terms_accepted': True
                                    },
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 1)

    def test_user_cannot_change_accommodation_after_paid(self):
        create_user_preferences(user=self.normal,
                                zosia=self.zosia,
                                accommodation_day_1=False,
                                shirt_size='M',
                                payment_accepted=True)
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 1)
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.post(self.url,
                                    data={
                                        'accommodation_day_1': True,
                                        'shirt_size': 'M',
                                        'shirt_type': 'f',
                                        'contact': 'fb: me',
                                        'terms_accepted': True
                                    },
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        prefs = UserPreferences.objects.filter(user=self.normal).first()
        self.assertFalse(prefs.accommodation_day_1)
        # Sanity check ;)
        self.assertEqual(prefs.shirt_size, 'M')
