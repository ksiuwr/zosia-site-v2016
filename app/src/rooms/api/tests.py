# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from conferences.test_helpers import new_user, new_zosia, user_preferences
from rooms.test_helpers import new_room


class RoomsAPIViewTestCase(APITestCase):
    def setUp(self):
        super().setUp()

        self.zosia = new_zosia(active=True)

        self.normal_1 = new_user(0)
        self.normal_2 = new_user(1)
        self.staff_1 = new_user(2, is_staff=True)
        self.staff_2 = new_user(3, is_staff=True)

        self.room_1 = new_room(111, capacity=2)
        self.room_2 = new_room(222, capacity=1)
        self.room_3 = new_room(333, capacity=3, hidden=True)


class JoinAPIViewTestCase(RoomsAPIViewTestCase):
    def setUp(self):
        super().setUp()
        self.url_1 = reverse("rooms_api_join", kwargs={"version": "v1", "pk": self.room_1.pk})
        self.url_2 = reverse("rooms_api_join", kwargs={"version": "v1", "pk": self.room_2.pk})
        self.url_3 = reverse("rooms_api_join", kwargs={"version": "v1", "pk": self.room_3.pk})

    def tearDown(self):
        self.client.force_authenticate(user=None)
        super().tearDown()

    def test_can_join_free_room(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_2, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.room_2.members_count, 1)
        self.assertIn(self.normal_1, self.room_2.members.all())

    def test_can_join_room_when_available_place(self):
        self.room_1.join(self.normal_2)

        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.room_1.members_count, 2)
        self.assertIn(self.normal_2, self.room_1.members.all())
        self.assertIn(self.normal_1, self.room_1.members.all())

    def test_cannot_join_without_active_zosia(self):
        self.client.force_authenticate(user=self.normal_1)

        self.zosia.active = False
        self.zosia.save()

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_join_without_registration(self):
        self.client.force_authenticate(user=self.normal_1)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_join_without_payment(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=False)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_join_after_registration_end(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.zosia.rooming_end = datetime.now().date() - timedelta(days=7)
        self.zosia.save()

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_join_before_registration_start(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.zosia.rooming_start = datetime.now().date() + timedelta(days=7)
        self.zosia.save()

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_join_locked_room(self):
        self.room_1.join(self.normal_2)
        self.room_1.set_lock(self.normal_2)

        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_join_locked_room_with_password(self):
        self.room_1.join(self.normal_2)
        self.room_1.set_lock(self.normal_2)

        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        data = {"user": self.normal_1.pk, "password": self.room_1.lock.password}
        response = self.client.post(self.url_1, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.room_1.members_count, 2)
        self.assertIn(self.normal_1, self.room_1.members.all())
        self.assertIn(self.normal_2, self.room_1.members.all())

    def test_cannot_join_full_room(self):
        self.room_2.join(self.normal_2)

        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_2, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# REUSE THESE TESTS LATER
# class UnlockViewTestCase(RoomsViewTestCase):
#     def setUp(self):
#         super().setUp()
#         self.url = reverse("rooms_unlock")
#         self.login()
#         self.register(payment_accepted=True)
#
#     def test_can_unlock_owned_room(self):
#         self.room_1.join(self.normal_1)
#         self.room_1.set_lock(self.normal_1)
#         response = self.post()
#         self.assertEqual(response.status_code, 200)
#         self.room_1.refresh_from_db()
#         self.assertFalse(self.room_1.is_locked)
#
#     def test_cannot_unlock_not_owned_room(self):
#         self.room_1.join(self.normal_2)
#         self.room_1.set_lock(self.normal_2)
#         self.room_1.join(self.normal_1, password=self.room_1.lock.password)
#         response = self.post()
#         self.assertEqual(response.status_code, 403)
#         self.room_1.refresh_from_db()
#         self.assertTrue(self.room_1.is_locked)
#
#     def test_cannot_unlock_after_rooming_end(self):
#         self.room_1.join(self.normal_1)
#         self.room_1.set_lock(self.normal_1)
#         self.zosia.rooming_end = datetime.now().date() - timedelta(7)
#         self.zosia.save()
#         response = self.post()
#         self.assertEqual(response.status_code, 400)
#         self.room_1.refresh_from_db()
#         self.assertTrue(self.room_1.is_locked)
