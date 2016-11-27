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


def new_zosia(**kwargs):
    now = datetime.now() + timedelta(1)
    place, _ = Place.objects.get_or_create(
        name='Mieszko',
        address='FooBar@Katowice'
    )
    defaults = {
        'active': False,
        'start_date': now,
        'place': place
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

    def test_post_user_not_registered(self):
        pass

    def test_post_user_already_registered(self):
        pass
