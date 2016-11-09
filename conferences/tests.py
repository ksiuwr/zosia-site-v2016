from django.test import TestCase
from django.core.exceptions import ValidationError
from conferences.models import Zosia, Place
from datetime import datetime, timedelta


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
