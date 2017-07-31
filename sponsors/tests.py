from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.shortcuts import reverse
from django.test import TestCase
from sponsors.models import Sponsor
from sponsors.forms import SponsorForm
import os


User = get_user_model()


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
        sponsor = Sponsor(name="Foo", url="http://google.com",
                          logo=self.image.name)
        try:
            sponsor.full_clean()
        except ValidationError:
            self.fail("Full clean failed")
        sponsor.save()
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

    def test_toggle_active(self):
        sponsor = Sponsor(url="http://google.com", logo=self.image.name,
                          is_active=True, name="Bar")
        sponsor.save()
        self.assertTrue(sponsor.is_active)
        sponsor.toggle_active()
        self.assertFalse(sponsor.is_active)
        sponsor.toggle_active()
        self.assertTrue(sponsor.is_active)


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


class ViewsTestCase(SponsorTestCase):
    def setUp(self):
        super().setUp()
        self.staff = User.objects.create_user('paul@thebeatles.com',
                                              'paulpassword')
        self.staff.is_staff = True
        self.staff.save()

        self.normal = User.objects.create_user('lennon@thebeatles.com',
                                               'johnpassword')
        self.normal.save()

    def test_index_get_no_user(self):
        response = self.client.get(reverse('sponsors_index'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/sponsors/')

    def test_index_get_normal_user(self):
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.get(reverse('sponsors_index'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/sponsors/')

    def test_index_get_staff_user(self):
        self.client.login(email='paul@thebeatles.com', password='paulpassword')
        response = self.client.get(reverse('sponsors_index'), follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(list(context['objects']), list(Sponsor.objects.all()))

    def test_add_get_staff_user(self):
        self.client.login(email='paul@thebeatles.com', password='paulpassword')
        response = self.client.get(reverse('sponsors_add'), follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(context['form'].__class__, SponsorForm)

    def test_edit_get_staff_user(self):
        self.client.login(email='paul@thebeatles.com', password='paulpassword')
        sponsor = Sponsor(name='foo', url='http://google.com', logo=self.image)
        sponsor.save()
        response = self.client.get(reverse('sponsors_edit',
                                           kwargs={'sponsor_id': sponsor.id}),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(context['form'].__class__, SponsorForm)
        self.assertEqual(context['object'], sponsor)

    def test_sposor_toggle_active(self):
        self.client.login(email='paul@thebeatles.com', password='paulpassword')
        sponsor = Sponsor(name='foo', url='http://google.com', logo=self.image)
        sponsor.save()
        self.assertFalse(sponsor.is_active)
        response = self.client.post(reverse('sponsors_toggle_active'),
                                    {'key': sponsor.id}, follow=True)
        sponsor.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(sponsor.is_active)
