from django.shortcuts import reverse
from django.test import TestCase

from organizers.forms import OrganizerForm
from organizers.models import OrganizerContact
from utils.constants import UserInternals
from utils.test_helpers import create_user, create_zosia, user_login


class FormTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.organizer = create_user(0, person_type=UserInternals.PERSON_ORGANIZER)
        self.normal = create_user(1, person_type=UserInternals.PERSON_NORMAL)
        self.zosia = create_zosia()

    def test_no_data(self):
        form = OrganizerForm()
        self.assertFalse(form.is_valid())

    def test_create_object(self):
        count = OrganizerContact.objects.count()
        form = OrganizerForm(
            {'zosia': self.zosia.pk, 'user': self.organizer.pk, 'phone_number': '123456789'})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(count + 1, OrganizerContact.objects.count())

    def test_valid_phone_number(self):
        form = OrganizerForm(
            {'zosia': self.zosia.pk, 'user': self.organizer.pk, 'phone_number': '123s56A89'})
        self.assertFalse(form.is_valid())

    def test_user_must_be_organizer(self):
        form = OrganizerForm(
            {'zosia': self.zosia.pk, 'user': self.normal.pk, 'phone_number': '123456789'})
        self.assertFalse(form.is_valid())


class ViewsTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.staff = create_user(0, person_type=UserInternals.PERSON_NORMAL, is_staff=True)
        self.normal = create_user(1, person_type=UserInternals.PERSON_NORMAL)
        self.zosia = create_zosia()

    def test_index_get_no_user(self):
        response = self.client.get(reverse('organizers_index'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/organizers/')

    def test_index_get_normal_user(self):
        self.client.login(**user_login(self.normal))
        response = self.client.get(reverse('organizers_index'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/organizers/')

    def test_index_get_staff_user(self):
        self.client.login(**user_login(self.staff))
        response = self.client.get(reverse('organizers_index'), follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(list(context['objects']), list(OrganizerContact.objects.all()))

    def test_add_get_staff_user(self):
        self.client.login(**user_login(self.staff))
        response = self.client.get(reverse('organizers_add'), follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(context['form'].__class__, OrganizerForm)

    def test_edit_get_staff_user(self):
        self.client.login(**user_login(self.staff))
        organizer = OrganizerContact(zosia=self.zosia, user=self.staff, phone_number='123456789')
        organizer.save()
        response = self.client.get(reverse('organizers_edit',
                                           kwargs={'contact_id': organizer.id}),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(context['form'].__class__, OrganizerForm)
        self.assertIsNone(context['form'].fields.get('user'))
        self.assertEqual(context['object'], organizer)
