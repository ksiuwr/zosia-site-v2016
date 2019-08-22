# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from conferences.test_helpers import new_user, new_zosia, user_preferences
from rooms.test_helpers import RoomAssertions, new_room

room_assertions = RoomAssertions()


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

    def test_user_can_join_free_room(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_2, data, format="json")
        self.room_2.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertJoined(self.normal_1, self.room_2)

    def test_user_can_join_room_when_available_place(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.room_1.join(self.normal_2)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertJoined(self.normal_2, self.room_1)
        room_assertions.assertJoined(self.normal_1, self.room_1)

    def test_user_can_join_other_room(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.room_1.join(self.normal_1)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_2, data, format="json")
        self.room_1.refresh_from_db()
        self.room_2.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertEmpty(self.room_1)
        room_assertions.assertJoined(self.normal_1, self.room_2)

    def test_user_cannot_join_without_active_zosia(self):
        self.client.force_authenticate(user=self.normal_1)

        self.zosia.active = False
        self.zosia.save()

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_join_without_registration(self):
        self.client.force_authenticate(user=self.normal_1)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_join_without_payment(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=False)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_join_after_rooming_ends(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.zosia.rooming_end = datetime.now().date() - timedelta(days=7)
        self.zosia.save()

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_join_before_rooming_starts(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.zosia.rooming_start = datetime.now().date() + timedelta(days=7)
        self.zosia.save()

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_join_locked_room(self):
        self.room_1.join(self.normal_2)
        self.room_1.set_lock(self.normal_2)

        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_join_locked_room_with_password(self):
        self.room_1.join(self.normal_2)
        self.room_1.set_lock(self.normal_2)

        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        data = {"user": self.normal_1.pk, "password": self.room_1.lock.password}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertJoined(self.normal_1, self.room_1)
        room_assertions.assertJoined(self.normal_2, self.room_1)

    def test_user_cannot_join_full_room(self):
        self.room_2.join(self.normal_2)

        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_2, data, format="json")
        self.room_2.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_join_hidden_room(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_3, data, format="json")
        self.room_3.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_add_user_to_free_room(self):
        self.client.force_authenticate(user=self.staff_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_2, data, format="json")
        self.room_2.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertJoined(self.normal_1, self.room_2)

    def test_staff_can_add_user_to_hidden_room(self):
        self.client.force_authenticate(user=self.staff_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_3, data, format="json")
        self.room_3.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertJoined(self.normal_1, self.room_3)

    def test_staff_can_add_user_to_locked_room(self):
        self.room_1.join(self.normal_2)
        self.room_1.set_lock(self.normal_2)

        self.client.force_authenticate(user=self.staff_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertJoined(self.normal_1, self.room_1)
        room_assertions.assertJoined(self.normal_2, self.room_1)

    def test_staff_cannot_add_user_to_full_room(self):
        self.room_2.join(self.normal_2)

        self.client.force_authenticate(user=self.staff_2)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_2, data, format="json")
        self.room_2.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_add_user_to_room_after_rooming_ends(self):
        self.client.force_authenticate(user=self.staff_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.zosia.rooming_end = datetime.now().date() - timedelta(days=7)
        self.zosia.save()

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertJoined(self.normal_1, self.room_1)

    def test_staff_can_add_user_to_room_before_rooming_starts(self):
        self.client.force_authenticate(user=self.staff_2)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.zosia.rooming_start = datetime.now().date() + timedelta(days=7)
        self.zosia.save()

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertJoined(self.normal_1, self.room_1)


class LeaveAPIViewTestCase(RoomsAPIViewTestCase):
    def setUp(self):
        super().setUp()
        self.url_1 = reverse("rooms_api_leave", kwargs={"version": "v1", "pk": self.room_1.pk})
        self.url_2 = reverse("rooms_api_leave", kwargs={"version": "v1", "pk": self.room_2.pk})

    def test_user_can_leave_joined_room(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.room_1.join(self.normal_1)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertEmpty(self.room_1)

    def test_owner_can_leave_locked_room_then_unlocks(self):
        self.client.force_authenticate(user=self.normal_2)
        user_preferences(user=self.normal_2, zosia=self.zosia, payment_accepted=True)

        self.room_2.join(self.normal_2)
        self.room_2.set_lock(self.normal_2)

        data = {"user": self.normal_2.pk}
        response = self.client.post(self.url_2, data, format="json")
        self.room_2.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertEmpty(self.room_2)
        room_assertions.assertUnlocked(self.room_2)

    def test_not_owner_can_leave_locked_room_then_lock_remains(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.room_1.join(self.normal_2)
        self.room_1.join(self.normal_2)
        self.room_1.set_lock(self.normal_2)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.room_1.members_count, 1)
        room_assertions.assertLocked(self.room_1, self.normal_2)

    def test_staff_can_remove_user_from_room(self):
        self.client.force_authenticate(user=self.staff_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.room_1.join(self.normal_1)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertEmpty(self.room_1)


class LockAPIViewTestCase(RoomsAPIViewTestCase):
    def setUp(self):
        super().setUp()
        self.url_1 = reverse("rooms_api_lock", kwargs={"version": "v1", "pk": self.room_1.pk})
        self.url_2 = reverse("rooms_api_lock", kwargs={"version": "v1", "pk": self.room_2.pk})
        self.url_3 = reverse("rooms_api_lock", kwargs={"version": "v1", "pk": self.room_3.pk})

    def test_user_can_lock_room_after_joining(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.room_1.join(self.normal_1)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertLocked(self.room_1, self.normal_1)

    def test_user_cannot_lock_room_without_joining(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_following_user_can_join_and_lock(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.room_1.join(self.normal_2)
        self.room_1.join(self.normal_1)

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertLocked(self.room_1, self.normal_1)

    def test_staff_can_lock_room_with_expiration_date(self):
        self.client.force_authenticate(user=self.staff_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.room_1.join(self.normal_1)

        expiration_date = timezone.make_aware(datetime.now() + timedelta(days=1))
        data = {"user": self.normal_1.pk, "expiration_date": expiration_date}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertLocked(self.room_1, self.normal_1)
        self.assertEqual(self.room_1.lock.expiration_date, expiration_date)

    def test_staff_can_lock_locked_room(self):
        self.client.force_authenticate(user=self.staff_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)

        expiration_date = timezone.make_aware(datetime.now() + timedelta(days=5))
        data = {"user": self.normal_1.pk, "expiration_date": expiration_date}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertLocked(self.room_1, self.normal_1)
        self.assertEqual(self.room_1.lock.expiration_date, expiration_date)

    def test_staff_can_lock_hidden_room(self):
        self.client.force_authenticate(user=self.staff_2)
        user_preferences(user=self.normal_2, zosia=self.zosia, payment_accepted=True)

        self.room_3.join(self.normal_2, self.staff_2)

        data = {"user": self.normal_2.pk}
        response = self.client.post(self.url_3, data, format="json")
        self.room_3.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertLocked(self.room_3, self.normal_2)

    def test_staff_can_lock_before_rooming_starts(self):
        self.client.force_authenticate(user=self.staff_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.room_1.join(self.normal_1)

        self.zosia.rooming_start = datetime.now().date() + timedelta(days=7)
        self.zosia.save()

        data = {"user": self.normal_1.pk}
        response = self.client.post(self.url_1, data, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertLocked(self.room_1, self.normal_1)


class UnlockAPIViewTestCase(RoomsAPIViewTestCase):
    def setUp(self):
        super().setUp()
        self.url_1 = reverse("rooms_api_unlock", kwargs={"version": "v1", "pk": self.room_1.pk})
        self.url_2 = reverse("rooms_api_unlock", kwargs={"version": "v1", "pk": self.room_2.pk})

    def test_owner_can_unlock_owned_room(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)

        response = self.client.post(self.url_1, {}, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertUnlocked(self.room_1)

    def test_user_cannot_unlock_not_owned_room(self):
        self.client.force_authenticate(user=self.normal_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.room_1.join(self.normal_2)
        self.room_1.set_lock(self.normal_2)
        self.room_1.join(self.normal_1, password=self.room_1.lock.password)

        response = self.client.post(self.url_1, {}, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        room_assertions.assertLocked(self.room_1, self.normal_2)

    def test_user_can_unlock_after_rooming_ends(self):
        self.client.force_authenticate(user=self.normal_2)
        user_preferences(user=self.normal_2, zosia=self.zosia, payment_accepted=True)

        self.room_2.join(self.normal_2)
        self.room_2.set_lock(self.normal_2)

        self.zosia.rooming_end = datetime.now().date() - timedelta(days=7)
        self.zosia.save()

        response = self.client.post(self.url_2, {}, format="json")
        self.room_2.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        room_assertions.assertLocked(self.room_2, self.normal_2)

    def test_staff_can_unlock_room(self):
        self.client.force_authenticate(user=self.staff_1)
        user_preferences(user=self.normal_1, zosia=self.zosia, payment_accepted=True)

        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)

        response = self.client.post(self.url_1, {}, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.room_1.is_locked)

    def test_staff_can_unlock_after_rooming_ends(self):
        self.client.force_authenticate(user=self.staff_2)
        user_preferences(user=self.normal_2, zosia=self.zosia, payment_accepted=True)

        self.room_2.join(self.normal_2)
        self.room_2.set_lock(self.normal_2)

        self.zosia.rooming_end = datetime.now().date() - timedelta(days=7)
        self.zosia.save()

        response = self.client.post(self.url_2, {}, format="json")
        self.room_2.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertUnlocked(self.room_2)


class HidingAPIViewTestCase(RoomsAPIViewTestCase):
    def test_staff_can_hide_room(self):
        self.client.force_authenticate(user=self.staff_1)

        url = reverse("rooms_api_hide", kwargs={"version": "v1", "pk": self.room_1.pk})
        response = self.client.post(url, {}, format="json")
        self.room_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertHidden(self.room_1)

    def test_staff_can_unhide_room(self):
        self.client.force_authenticate(user=self.staff_2)

        url = reverse("rooms_api_unhide", kwargs={"version": "v1", "pk": self.room_3.pk})
        response = self.client.post(url, {}, format="json")
        self.room_3.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room_assertions.assertUnhidden(self.room_3)

    def test_user_cannot_hide_room(self):
        self.client.force_authenticate(user=self.normal_1)

        url = reverse("rooms_api_hide", kwargs={"version": "v1", "pk": self.room_2.pk})
        response = self.client.post(url, {}, format="json")
        self.room_2.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_unhide_room(self):
        self.client.force_authenticate(user=self.normal_2)

        url = reverse("rooms_api_unhide", kwargs={"version": "v1", "pk": self.room_3.pk})
        response = self.client.post(url, {}, format="json")
        self.room_3.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
