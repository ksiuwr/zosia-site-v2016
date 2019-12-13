from django.test import TestCase
from django.urls import reverse

from conferences.test_helpers import PRICE_BASE, PRICE_BREAKFAST, PRICE_DINNER, PRICE_FULL, \
    create_user, create_user_preferences, create_zosia
from users.forms import UserPreferencesAdminForm, UserPreferencesForm
from users.models import UserPreferences


class UserPreferencesTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.normal = create_user(0)
        self.staff = create_user(1, is_staff=True)
        self.zosia = create_zosia(active=True)


class UserPreferencesModelTestCase(UserPreferencesTestCase):
    def makeUserPrefs(self, **override):
        defaults = {
            'user': self.normal,
            'zosia': self.zosia,
            'contact': 'fb: me',
            'shirt_size': 'S',
            'shirt_type': 'f',
            'terms_accepted': True
        }
        defaults.update(**override)
        return UserPreferences(**defaults)

    def test_price_base(self):
        user_prefs = self.makeUserPrefs(
            accommodation_day_1=False,
            dinner_day_1=False,
            breakfast_day_2=False,
            accommodation_day_2=False,
            dinner_day_2=False,
            breakfast_day_3=False,
            accommodation_day_3=False,
            dinner_day_3=False,
            breakfast_day_4=False,
        )

        self.assertEqual(user_prefs.price, PRICE_BASE)

    def test_price_whole_day(self):
        user_prefs = self.makeUserPrefs(
            accommodation_day_1=True,
            dinner_day_1=True,
            breakfast_day_2=True,
            accommodation_day_2=False,
            dinner_day_2=False,
            breakfast_day_3=False,
            accommodation_day_3=False,
            dinner_day_3=False,
            breakfast_day_4=False,
        )

        self.assertEqual(user_prefs.price,
                         PRICE_BASE + PRICE_FULL)

    def test_price_day_with_dinner(self):
        user_prefs = self.makeUserPrefs(
            accommodation_day_1=True,
            dinner_day_1=True,
            breakfast_day_2=False,
            accommodation_day_2=False,
            dinner_day_2=False,
            breakfast_day_3=False,
            accommodation_day_3=False,
            dinner_day_3=False,
            breakfast_day_4=False,
        )

        self.assertEqual(user_prefs.price,
                         PRICE_BASE + PRICE_DINNER)

    def test_price_day_with_breakfast(self):
        user_prefs = self.makeUserPrefs(
            accommodation_day_1=True,
            dinner_day_1=False,
            breakfast_day_2=True,
            accommodation_day_2=False,
            dinner_day_2=False,
            breakfast_day_3=False,
            accommodation_day_3=False,
            dinner_day_3=False,
            breakfast_day_4=False,
        )

        self.assertEqual(user_prefs.price,
                         PRICE_BASE + PRICE_BREAKFAST)

    def test_full_price(self):
        user_prefs = self.makeUserPrefs(
            accommodation_day_1=True,
            dinner_day_1=True,
            breakfast_day_2=True,
            accommodation_day_2=True,
            dinner_day_2=True,
            breakfast_day_3=True,
            accommodation_day_3=True,
            dinner_day_3=True,
            breakfast_day_4=True,
        )

        self.assertEqual(user_prefs.price,
                         PRICE_BASE + 3 * PRICE_FULL)

    def test_price_with_everything_except_last_breakfast(self):
        user_prefs = self.makeUserPrefs(
            accommodation_day_1=True,
            dinner_day_1=True,
            breakfast_day_2=True,
            accommodation_day_2=True,
            dinner_day_2=True,
            breakfast_day_3=True,
            accommodation_day_3=True,
            dinner_day_3=True,
            breakfast_day_4=False,
        )

        self.assertEqual(user_prefs.price,
                         PRICE_BASE + 2 * PRICE_FULL + PRICE_DINNER)

    def test_price_for_whole_second_day(self):
        user_prefs = self.makeUserPrefs(
            accommodation_day_1=False,
            dinner_day_1=False,
            breakfast_day_2=False,
            accommodation_day_2=True,
            dinner_day_2=True,
            breakfast_day_3=True,
            accommodation_day_3=False,
            dinner_day_3=False,
            breakfast_day_4=False,
        )

        self.assertEqual(user_prefs.price,
                         PRICE_BASE + PRICE_FULL)

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
            'terms_accepted': True
        }
        defaults.update(**override)
        return UserPreferencesForm(self.normal, defaults)

    def test_basic_form(self):
        self.assertTrue(self.makeUserPrefsForm().is_valid())

    def test_accommodation_must_be_chosen_for_dinner_or_breakfast(self):
        form = self.makeUserPrefsForm(breakfast_day_2=True, accommodation_day_2=False)
        self.assertFalse(form.is_valid())


class UserPreferencesIndexTestCase(UserPreferencesTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('user_preferences_index')

    def test_index_get_no_user(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/accounts/preferences/')

    def test_index_get_normal_user(self):
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/accounts/preferences/')

    def test_index_get_staff_user(self):
        self.client.login(email="starr@thebeatles.com", password='ringopassword')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(list(context['objects']), list(UserPreferences.objects.all()))

    def test_index_get_staff_user_multiple_zosias(self):
        another_zosia = create_zosia()
        create_user_preferences(user=self.normal, zosia=another_zosia)
        create_user_preferences(user=self.normal, zosia=self.zosia)
        create_user_preferences(user=self.staff, zosia=self.zosia)
        self.client.login(email="starr@thebeatles.com", password='ringopassword')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(list(context['objects']),
                         list(UserPreferences.objects.filter(zosia=self.zosia).all()))


class UserPreferencesAdminEditTestCase(UserPreferencesTestCase):
    def setUp(self):
        super().setUp()
        self.user_prefs = create_user_preferences(user=self.normal, zosia=self.zosia)
        self.url = reverse('user_preferences_admin_edit')

    def test_post_no_user(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/accounts/preferences/admin_edit/')

    def test_post_normal_user(self):
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.post(self.url,
                                    {'key': self.user_prefs.pk},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/accounts/preferences/admin_edit/')

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


class UserPreferencesEditTestCase(UserPreferencesTestCase):
    def setUp(self):
        super().setUp()
        self.user_prefs = create_user_preferences(user=self.normal, zosia=self.zosia, contact='foo')
        self.url = reverse('user_preferences_edit', kwargs={'pk': self.user_prefs.pk})

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
                                        'bonus_minutes': 0,
                                        'terms_accepted': True
                                    },
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        prefs = UserPreferences.objects.filter(pk=self.user_prefs.pk).first()
        self.assertEqual(prefs.shirt_size, 'XXL')
        self.assertEqual(prefs.shirt_type, 'f')
