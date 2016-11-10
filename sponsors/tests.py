from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import ValidationError
from django.test import TestCase
from sponsors.models import Sponsor


class ModelTestCase(TestCase):
    def setUp(self):
        self.image = SimpleUploadedFile('foo.img', b'bar')

    def test_create_object(self):
        count = Sponsor.objects.count()
        Sponsor.objects.create(name="Foo", url="http://google.com",
                               logo=self.image)
        self.assertEqual(count + 1, Sponsor.objects.count())

    def test_object_must_have_name(self):
        sponsor = Sponsor(url="http://google.com", logo=self.image)
        with self.assertRaises(ValidationError):
            sponsor.full_clean()

    def test_must_have_image(self):
        sponsor = Sponsor(url="http://google.com", name="foo")
        with self.assertRaises(ValidationError):
            sponsor.full_clean()

    def test_do_not_need_url(self):
        count = Sponsor.objects.count()
        sponsor = Sponsor(name='foo', logo=self.image)
        sponsor.full_clean()
        sponsor.save()
        self.assertEqual(count + 1, Sponsor.objects.count())

    def test_object_must_have_valid_url(self):
        sponsor = Sponsor(name="foo", logo=self.image, url="goo.baz")
        with self.assertRaises(ValidationError):
            sponsor.full_clean()

    def test_str(self):
        sponsor = Sponsor(url="http://google.com", logo=self.image,
                          is_active=True, name="Bar")
        sponsor.save()
        self.assertEqual(str(sponsor), "Bar")
