from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import ValidationError
from django.test import TestCase
from sponsors.models import Sponsor
from sponsors.forms import SponsorForm
import os


class SponsorTestCase(TestCase):
    def setUp(self):
        img = open(os.path.join(settings.BASE_DIR, '..',
                                'static/imgs/zosia.png'), 'rb')
        self.image = SimpleUploadedFile(
            name='up.png', content=img.read(),
            content_type='image/png')


class ModelTestCase(SponsorTestCase):

    def test_create_object(self):
        count = Sponsor.objects.count()
        Sponsor.objects.create(name="Foo", url="http://google.com",
                               logo=self.image.name)
        self.assertEqual(count + 1, Sponsor.objects.count())

    def test_object_must_have_name(self):
        sponsor = Sponsor(url="http://google.com", logo=self.image.name)
        with self.assertRaises(ValidationError):
            sponsor.full_clean()

    def test_must_have_image(self):
        sponsor = Sponsor(url="http://google.com", name="foo")
        with self.assertRaises(ValidationError):
            sponsor.full_clean()

    def test_do_not_need_url(self):
        count = Sponsor.objects.count()
        sponsor = Sponsor(name='foo', logo=self.image.name)
        sponsor.full_clean()
        sponsor.save()
        self.assertEqual(count + 1, Sponsor.objects.count())

    def test_object_must_have_valid_url(self):
        sponsor = Sponsor(name="foo", logo=self.image.name, url="goo.baz")
        with self.assertRaises(ValidationError):
            sponsor.full_clean()

    def test_str(self):
        sponsor = Sponsor(url="http://google.com", logo=self.image.name,
                          is_active=True, name="Bar")
        sponsor.save()
        self.assertEqual(str(sponsor), "Bar")


class FormTestCase(SponsorTestCase):
    def test_no_data(self):
        form = SponsorForm()
        self.assertFalse(form.is_valid())

    def test_create_object(self):
        count = Sponsor.objects.count()
        form = SponsorForm({'name': 'foo', 'url': 'http://google.com'},
                           {'logo': self.image})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(count + 1, Sponsor.objects.count())

    def test_url_must_be_valid(self):
        form = SponsorForm({'name': 'foo', 'url': 'barbaz'},
                           {'logo': self.image})
        self.assertFalse(form.is_valid())