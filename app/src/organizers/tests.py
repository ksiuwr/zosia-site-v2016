from django.shortcuts import reverse
from django.test import TestCase

from utils.test_helpers import create_zosia
from utils.constants import UserInternals

from organizers.forms import OrganizerForm
from organizers.models import OrganizerContact
from users.models import User

class FormTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.staff = User.objects.create_user('paul@thebeatles.com',
                                              'paulpassword')
        self.staff.is_staff = True
        self.staff.save()

        self.normal = User.objects.create_user('lennon@thebeatles.com',
                                               'johnpassword')
        self.normal.save()

        self.zosia = create_zosia()

    def test_no_data(self):
        form = OrganizerForm()
        self.assertFalse(form.is_valid())

    def test_create_object(self):
        count = OrganizerContact.objects.count()
        form = OrganizerForm({'zosia': self.zosia.pk, 'user': self.staff.pk, 'phone_number': '123456789'})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(count + 1, OrganizerContact.objects.count())

    def test_valid_phone_number(self):
        form = OrganizerForm({'zosia': self.zosia.pk, 'user': self.staff.pk, 'phone_number': '123s56A89'})
        self.assertFalse(form.is_valid())

    def test_organizer_must_be_staff(self):
        form = OrganizerForm({'zosia': self.zosia.pk, 'user': self.normal.pk, 'phone_number': '123456789'})
        self.assertFalse(form.is_valid())

class ViewsTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.staff = User.objects.create_user('paul@thebeatles.com',
                                              'paulpassword')
        self.staff.is_staff = True
        self.staff.save()

        self.normal = User.objects.create_user('lennon@thebeatles.com',
                                               'johnpassword')
        self.normal.save()

        self.zosia = create_zosia()

    def test_index_get_no_user(self):
        response = self.client.get(reverse('organizers_index'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/organizers/')

    def test_index_get_normal_user(self):
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.get(reverse('organizers_index'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/organizers/')

    def test_index_get_staff_user(self):
        self.client.login(email='paul@thebeatles.com', password='paulpassword')
        response = self.client.get(reverse('organizers_index'), follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(list(context['objects']), list(OrganizerContact.objects.all()))

    def test_add_get_staff_user(self):
        self.client.login(email='paul@thebeatles.com', password='paulpassword')
        response = self.client.get(reverse('organizers_add'), follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(context['form'].__class__, OrganizerForm)

    def test_edit_get_staff_user(self):
        self.client.login(email='paul@thebeatles.com', password='paulpassword')
        organizer = OrganizerContact(zosia=self.zosia, user=self.staff, phone_number='123456789')
        organizer.save()
        response = self.client.get(reverse('organizers_edit',
                                           kwargs={'user_id': organizer.user.pk}),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(context['form'].__class__, OrganizerForm)
        self.assertIsNone(context['form'].fields.get('user'))
        self.assertEqual(context['object'], organizer)

    