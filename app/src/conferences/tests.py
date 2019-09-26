from datetime import timedelta
from unittest import skip

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import reverse
from django.test import TestCase

from conferences.forms import UserPreferencesAdminForm, UserPreferencesForm
from conferences.models import Bus, UserPreferences, Zosia
from conferences.test_helpers import (PRICE_BASE, PRICE_BONUS, PRICE_DINNER, create_bus,
                                      create_user, create_user_preferences, create_zosia, )
from users.models import Organization
from utils.time_manager import TimeManager

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
        self.active.rooming_start = TimeManager.now()
        self.active.save()
        user_prefs = create_user_preferences(payment_accepted=True, bonus_minutes=0,
                                             user=create_user(0),
                                             zosia=self.active)

        result = self.active.can_user_choose_room(user_prefs)

        self.assertTrue(result)

    def test_can_user_choose_room_when_before_user_start_time(self):
        self.active.rooming_start = TimeManager.time_point(2016, 12, 23, 0, 0)
        self.active.save()
        user_prefs = create_user_preferences(payment_accepted=True, bonus_minutes=1,
                                             user=create_user(0),
                                             zosia=self.active)

        result = self.active.can_user_choose_room(user_prefs,
                                                  now=TimeManager.time_point(2016, 12, 22, 23, 58))
        self.assertFalse(result)

    def test_can_user_choose_room_when_after_user_start_time(self):
        self.active.rooming_start = TimeManager.time_point(2016, 12, 23, 0, 0)
        self.active.save()
        user_prefs = create_user_preferences(payment_accepted=True, bonus_minutes=3,
                                             user=create_user(0),
                                             zosia=self.active)

        result = self.active.can_user_choose_room(user_prefs,
                                                  now=TimeManager.time_point(2016, 12, 22, 23, 58))
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
        self.normal = create_user(0)
        self.zosia = create_zosia()

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

    def test_toggle_payment_accepted(self):
        user_prefs = self.makeUserPrefs(
            payment_accepted=True
        )
        self.assertTrue(user_prefs.payment_accepted)
        user_prefs.toggle_payment_accepted()
        self.assertFalse(user_prefs.payment_accepted)
        user_prefs.toggle_payment_accepted()
        self.assertTrue(user_prefs.payment_accepted)


class UserPreferencesFormTestCase(TestCase):
    def makeUserPrefsForm(self, **override):
        self.normal = create_user(0)
        defaults = {
            'contact': 'fb: me',
            'shirt_size': 'S',
            'shirt_type': 'f',
            'accepted': True
        }
        defaults.update(**override)
        return UserPreferencesForm(self.normal, defaults)

    def test_basic_form(self):
        self.assertTrue(self.makeUserPrefsForm().is_valid())

    def test_accomodation_must_be_chosen_for_dinner_or_breakfast(self):
        form = self.makeUserPrefsForm(breakfast_2=True, accomodation_2=False)
        self.assertFalse(form.is_valid())


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
                                        'accepted': True
                                    },
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 1)

    def test_post_user_already_registered(self):
        UserPreferences.objects.create(user=self.normal, zosia=self.zosia)
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 1)
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.post(self.url,
                                    data={
                                        'contact': 'fb: me',
                                        'shirt_size': 'S',
                                        'shirt_type': 'f',
                                        'accepted': True
                                    },
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 1)

    def test_user_cannot_change_accomodation_after_paid(self):
        UserPreferences.objects.create(user=self.normal,
                                       zosia=self.zosia,
                                       accomodation_day_1=False,
                                       shirt_size='M',
                                       payment_accepted=True)
        self.assertEqual(UserPreferences.objects.filter(user=self.normal).count(), 1)
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.post(self.url,
                                    data={
                                        'accomodation_day_1': True,
                                        'shirt_size': 'M',
                                        'shirt_type': 'f',
                                        'contact': 'fb: me',
                                        'accepted': True
                                    },
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        prefs = UserPreferences.objects.filter(user=self.normal).first()
        self.assertFalse(prefs.accomodation_day_1)
        # Sanity check ;)
        self.assertEqual(prefs.shirt_size, 'M')


class AdminUserPreferencesTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.normal = create_user(0)
        self.staff = create_user(1, is_staff=True)
        self.zosia = create_zosia(active=True)


class UserPreferencesIndexTestCase(AdminUserPreferencesTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('user_preferences_index')

    def test_index_get_no_user(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/user_preferences/')

    def test_index_get_normal_user(self):
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/user_preferences/')

    def test_index_get_staff_user(self):
        self.client.login(email="starr@thebeatles.com", password='ringopassword')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(list(context['objects']), list(UserPreferences.objects.all()))

    def test_index_get_staff_user_multiple_zosias(self):
        another_zosia = create_zosia()
        UserPreferences.objects.create(user=self.normal, zosia=another_zosia)
        UserPreferences.objects.create(user=self.normal, zosia=self.zosia)
        UserPreferences.objects.create(user=self.staff, zosia=self.zosia)
        self.client.login(email="starr@thebeatles.com", password='ringopassword')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(list(context['objects']),
                         list(UserPreferences.objects.filter(zosia=self.zosia).all()))


class UserPreferencesAdminEditTestCase(AdminUserPreferencesTestCase):
    def setUp(self):
        super().setUp()
        self.user_prefs = UserPreferences.objects.create(user=self.normal, zosia=self.zosia)
        self.url = reverse('user_preferences_admin_edit')

    def test_post_no_user(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/user_preferences_admin_edit/')

    def test_post_normal_user(self):
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.post(self.url,
                                    {'key': self.user_prefs.pk},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/user_preferences_admin_edit/')

    def test_post_staff_user_can_change_payment_status(self):
        self.client.login(email="starr@thebeatles.com", password='ringopassword')
        response = self.client.post(self.url,
                                    {'key': self.user_prefs.pk,
                                     'command': 'toggle_payment_accepted'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            UserPreferences.objects.filter(pk=self.user_prefs.pk).first().payment_accepted)

    def test_post_staff_user_can_bonus(self):
        self.client.login(email="starr@thebeatles.com", password='ringopassword')
        response = self.client.post(self.url,
                                    {'key': self.user_prefs.pk,
                                     'command': 'change_bonus',
                                     'bonus': 20},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            UserPreferences.objects.filter(pk=self.user_prefs.pk).first().bonus_minutes, 20)


class UserPreferencesEditTestCase(AdminUserPreferencesTestCase):
    def setUp(self):
        super().setUp()
        self.user_prefs = UserPreferences.objects.create(user=self.normal, zosia=self.zosia,
                                                         contact='foo')
        self.url = reverse('user_preferences_edit',
                           kwargs={'user_preferences_id': self.user_prefs.pk})

    def test_get_no_user(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=' + self.url)

    def test_get_normal_user(self):
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=' + self.url)

    def test_get_staff_user_returns_admin_form(self):
        self.client.login(email="starr@thebeatles.com", password='ringopassword')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(context['object'], self.user_prefs)
        self.assertEqual(context['form'].__class__, UserPreferencesAdminForm)

    def test_post_staff_user_will_change_prefs(self):
        self.client.login(email="starr@thebeatles.com", password='ringopassword')
        response = self.client.post(self.url,
                                    data={
                                        'shirt_size': 'XXL',
                                        'shirt_type': 'f',
                                        'contact': self.user_prefs.contact,
                                        'bonus_minutes': 0
                                    },
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        prefs = UserPreferences.objects.filter(pk=self.user_prefs.pk).first()
        self.assertEqual(prefs.shirt_size, 'XXL')
        self.assertEqual(prefs.shirt_type, 'f')
