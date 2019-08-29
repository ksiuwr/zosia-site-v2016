from datetime import timedelta
import json
from unittest import skip

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from conferences.test_helpers import new_user, new_zosia, user_login, user_preferences
from rooms.test_helpers import RoomAssertions, new_room
from utils.time_manager import TimeManager

room_assertions = RoomAssertions()


class RoomTestCase(TestCase):
    def refresh(self):
        self.room_1.refresh_from_db()
        self.room_2.refresh_from_db()

    def setUp(self):
        super().setUp()
        self.normal_1 = new_user(0)
        self.normal_2 = new_user(1)
        self.staff_1 = new_user(2, is_staff=True)
        self.staff_2 = new_user(3, is_staff=True)

        self.room_1 = new_room(111, capacity=2)
        self.room_2 = new_room(222, capacity=1)
        self.room_3 = new_room(333, capacity=3, hidden=True)

    # region join & leave

    def test_user_can_join_free_room(self):
        self.room_1.join(self.normal_1)
        room_assertions.assertJoined(self.normal_1, self.room_1)
        room_assertions.assertUnlocked(self.room_1)

    def test_locked_room_cannot_be_joined_without_password(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        room_assertions.assertLocked(self.room_1, self.normal_1)

        with self.assertRaises(ValidationError):
            self.room_1.join(self.normal_2)

    def test_locked_room_can_be_joined_with_password(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        room_assertions.assertLocked(self.room_1, self.normal_1)

        self.room_1.join(self.normal_2, password=self.room_1.lock.password)
        room_assertions.assertJoined(self.normal_2, self.room_1)

    def test_anyone_can_join_unlocked_room(self):
        self.room_1.join(self.normal_1)
        room_assertions.assertUnlocked(self.room_1)

        self.room_1.join(self.normal_2)
        room_assertions.assertJoined(self.normal_2, self.room_1)

    def test_full_room_cannot_be_joined(self):
        self.room_2.join(self.normal_1)

        with self.assertRaises(ValidationError):
            self.room_2.join(self.normal_2)

    def test_user_can_join_another_room_leaving_previous_room(self):
        self.room_1.join(self.normal_1)
        self.room_2.join(self.normal_1)
        self.assertEqual(self.room_1.members_count, 0)
        room_assertions.assertJoined(self.normal_1, self.room_2)

    def test_user_can_leave_not_joined_room(self):
        self.room_1.leave(self.normal_1)
        self.assertEqual(self.room_1.members_count, 0)

    def test_user_can_leave_joined_room(self):
        self.room_1.join(self.normal_1)
        self.room_1.leave(self.normal_1)
        self.assertEqual(self.room_1.members_count, 0)

    def test_staff_can_add_user_to_locked_room(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        room_assertions.assertLocked(self.room_1, self.normal_1)

        self.room_1.join(self.normal_2, self.staff_2)
        room_assertions.assertJoined(self.normal_2, self.room_1)

    def test_user_cannot_join_hidden_room(self):
        with self.assertRaises(ValidationError):
            self.room_3.join(self.normal_1)

    def test_staff_can_add_user_to_hidden_room(self):
        self.room_3.join(self.normal_2, self.staff_2)
        room_assertions.assertJoined(self.normal_2, self.room_3)

    # endregion
    # region lock & unlock

    def test_user_can_lock_room_after_joining(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        room_assertions.assertJoined(self.normal_1, self.room_1)
        room_assertions.assertLocked(self.room_1, self.normal_1)

    def test_user_cannot_lock_room_without_joining(self):
        with self.assertRaises(ValidationError):
            self.room_1.set_lock(self.normal_1)

    def test_following_user_can_join_and_lock(self):
        self.room_1.join(self.normal_1)
        self.room_1.join(self.normal_2)
        self.room_1.set_lock(self.normal_2)
        room_assertions.assertLocked(self.room_1, self.normal_2)

    def test_room_is_unlocked_after_expiration_date(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1,
                             expiration_date=TimeManager.timedelta_from_now(days=-30))
        room_assertions.assertUnlocked(self.room_1)

        self.room_1.join(self.normal_2)
        room_assertions.assertJoined(self.normal_2, self.room_1)

    def test_room_is_unlocked_after_joining_other_room(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        room_assertions.assertLocked(self.room_1, self.normal_1)

        self.room_2.join(self.normal_1)
        self.refresh()
        room_assertions.assertUnlocked(self.room_1)

    def test_room_remains_locked_after_not_owner_joins_other_room(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        self.room_1.join(self.normal_2, password=self.room_1.lock.password)
        room_assertions.assertJoined(self.normal_2, self.room_1)

        self.room_2.join(self.normal_2)
        self.refresh()
        room_assertions.assertLocked(self.room_1, self.normal_1)

    def test_room_is_unlocked_after_owner_leaves_room(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        room_assertions.assertLocked(self.room_1, self.normal_1)

        self.room_1.leave(self.normal_1)
        self.refresh()
        room_assertions.assertUnlocked(self.room_1)

    def test_room_remains_locked_after_not_owner_leaves_room(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        self.room_1.join(self.normal_2, password=self.room_1.lock.password)
        room_assertions.assertLocked(self.room_1, self.normal_1)

        self.room_1.leave(self.normal_2)
        self.refresh()
        room_assertions.assertLocked(self.room_1, self.normal_1)

    def test_user_can_unlock_unlocked_room(self):
        self.room_1.join(self.normal_1)
        self.room_1.unlock(self.normal_1)
        room_assertions.assertUnlocked(self.room_1)

    def test_owner_can_unlock_room(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        room_assertions.assertLocked(self.room_1, self.normal_1)

        self.room_1.unlock(self.normal_1)
        room_assertions.assertUnlocked(self.room_1)

    def test_not_owner_cannot_unlock_room(self):
        self.room_1.join(self.normal_1)
        self.room_1.join(self.normal_2)
        self.room_1.set_lock(self.normal_2)
        room_assertions.assertLocked(self.room_1, self.normal_2)

        with self.assertRaises(ValidationError):
            self.room_1.unlock(self.normal_1)

    def test_staff_can_lock_locked_room(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        room_assertions.assertLocked(self.room_1, self.normal_1)

        self.room_1.set_lock(self.normal_1, self.staff_1,
                             expiration_date=TimeManager.timedelta_from_now(days=-7))
        self.refresh()
        room_assertions.assertLocked(self.room_1, self.normal_1)

    def test_staff_can_unlock_room(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        room_assertions.assertLocked(self.room_1, self.normal_1)

        self.room_1.unlock(self.staff_1)
        room_assertions.assertUnlocked(self.room_1)

    def test_staff_can_lock_hidden_room(self):
        self.room_3.join(self.normal_1, self.staff_1)
        self.room_3.set_lock(self.normal_1, self.staff_1)
        room_assertions.assertLocked(self.room_3, self.normal_1)

    # endregion


class RoomsViewTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.zosia = new_zosia(active=True)

        self.normal_1 = new_user(0)
        self.normal_2 = new_user(1)

        self.room_1 = new_room(111, capacity=2)
        self.room_2 = new_room(222, capacity=1, hidden=True)

    def get(self, follow=True):
        return self.client.get(self.url, follow=follow)

    def post(self, follow=False, **kwargs):
        return self.client.post(self.url, follow=follow, **kwargs)

    def login(self):
        self.client.login(**user_login(self.normal_1))

    def register(self, **kwargs):
        return user_preferences(user=self.normal_1, zosia=self.zosia, **kwargs)


class IndexViewTestCase(RoomsViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('rooms_index')

    @skip("API changed. Needs rewrite")
    def test_can_room(self):
        self.login()
        self.register(payment_accepted=True)
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rooms/index.html')

    @skip("API changed. Needs rewrite")
    def test_cannot_room_without_login(self):
        response = self.get()
        self.assertRedirects(response, reverse('login') + '?next={}'.format(self.url))
        self.assertEqual(response.status_code, 200)

    @skip("API changed. Needs rewrite")
    def test_cannot_room_without_active_zosia(self):
        self.login()
        self.zosia.active = False
        self.zosia.save()
        response = self.get()
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(response.context['messages']._get()[0]), 1)

    @skip("API changed. Needs rewrite")
    def test_cannot_room_without_registration(self):
        self.login()
        response = self.get()
        self.assertRedirects(response,
                             reverse('user_zosia_register', kwargs={'zosia_id': self.zosia.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(response.context['messages']._get()[0]), 1)

    @skip("API changed. Needs rewrite")
    def test_cannot_room_without_payment(self):
        self.login()
        self.register()
        response = self.get()
        self.assertRedirects(response, reverse('accounts_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(response.context['messages']._get()[0]), 1)

    @skip("API changed. Needs rewrite")
    def test_cannot_room_before_rooming_open(self):
        self.zosia.rooming_start = self.zosia.rooming_start + timedelta(3)
        self.zosia.save()
        self.login()
        self.register(payment_accepted=True)
        response = self.get()
        self.assertRedirects(response, reverse('accounts_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(response.context['messages']._get()[0]), 1)

    @skip("API changed. Needs rewrite")
    def test_returns_no_hidden_rooms(self):
        self.login()
        self.register(payment_accepted=True)
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.room_1, response.context['rooms'])
        self.assertNotIn(self.room_2, response.context['rooms'])


class StatusViewTestCase(RoomsViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('rooms_status')

    def load_response(self, **kwargs):
        self.login()
        self.register(payment_accepted=True, **kwargs)
        response = self.get()
        self.assertEqual(response.status_code, 200)
        return json.loads(response.content.decode('utf-8'))

    def test_cannot_get_status_without_active_zosia(self):
        self.login()
        self.zosia.active = False
        self.zosia.save()
        response = self.get()
        self.assertEqual(response.status_code, 404)

    def test_cannot_get_status_without_registration(self):
        self.login()
        response = self.get()
        self.assertEqual(response.status_code, 404)

    def test_cannot_get_status_without_login(self):
        response = self.get(follow=False)
        self.assertEqual(response.status_code, 302)

    def test_status_returns_all_rooms(self):
        rooms = self.load_response()['rooms']
        room_pks = list(map(lambda x: x['id'], rooms))
        self.assertIn(self.room_1.pk, room_pks)

    def test_status_returns_no_hidden_rooms(self):
        rooms = self.load_response()['rooms']
        room_pks = list(map(lambda x: x['id'], rooms))
        self.assertNotIn(self.room_2, room_pks)

    def test_status_returns_own_room(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        rooms = self.load_response()['rooms']
        room = list(filter(lambda x: x['is_owned_by'], rooms))[0]['id']
        self.assertEqual(self.room_1.pk, room)

    def test_status_returns_can_room(self):
        can = self.load_response()['can_start_rooming']
        self.assertEqual(can, True)

    def test_status_returns_can_room_false_before_room_of_usering(self):
        can = self.load_response(bonus_minutes=-60 * 24 * 2)['can_start_rooming']
        self.assertEqual(can, False)
