from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from conferences.test_helpers import new_zosia, new_user
from .models import Room, UserRoom


def new_room(commit=True, **override):
    zosia = override['zosia'] or new_zosia()
    defaults = {
        'name': '109',
        'capacity': 0,
        'zosia': zosia,

    }
    defaults.update(**override)
    room = Room(**defaults)
    if commit:
        room.save()
    return room


class RoomTestCase(TestCase):
    def assertError(self, obj):
        self.assertEqual(type(obj), ValidationError)

    def assertJoined(self, obj, user, room):
        self.assertEqual(type(obj), UserRoom, obj.message if hasattr(obj, 'message') else None)
        self.assertTrue(obj.pk)
        self.assertEqual(obj.user, user)
        self.assertEqual(obj.room, room)

    def assertLocked(self, room):
        self.assertTrue(room.is_locked)

    def assertUnlocked(self, room):
        self.assertFalse(room.is_locked)

    def refresh(self):
        self.room_1.refresh_from_db()
        self.room_2.refresh_from_db()

    def setUp(self):
        self.zosia = new_zosia()

        self.normal_1 = new_user(0)
        self.normal_2 = new_user(1)

        self.room_1 = new_room(zosia=self.zosia, capacity=2)
        self.room_2 = new_room(zosia=self.zosia, capacity=1)

    def test_anyone_can_join_free_room(self):
        result = self.room_1.join(self.normal_1)
        self.assertJoined(result, self.normal_1, self.room_1)

    def test_room_is_locked_after_join(self):
        self.room_1.join(self.normal_1)
        self.assertLocked(self.room_1)

    def test_room_can_be_joined_without_locking(self):
        self.room_1.join(self.normal_1, lock=False)
        self.assertUnlocked(self.room_1)

    def test_following_user_can_join_and_lock(self):
        self.room_1.join(self.normal_1, lock=False)
        self.room_1.join(self.normal_2)
        self.assertLocked(self.room_1)

    def test_locked_room_cannot_be_joined(self):
        self.room_1.join(self.normal_1)
        self.assertLocked(self.room_1)
        result = self.room_1.join(self.normal_2)
        self.assertError(result)

    def test_locked_room_can_be_joined_with_password(self):
        self.room_1.join(self.normal_1)
        self.assertLocked(self.room_1)
        result = self.room_1.join(self.normal_2, password=self.room_1.lock.password)
        self.assertJoined(result, self.normal_2, self.room_1)

    def test_room_is_unlocked_after_expiration_time(self):
        self.room_1.join(self.normal_1, expiration=timedelta(-1))
        self.assertUnlocked(self.room_1)
        result = self.room_1.join(self.normal_2)
        self.assertJoined(result, self.normal_2, self.room_1)

    def test_anyone_can_join_unlocked_room(self):
        self.room_1.join(self.normal_1, expiration=timedelta(-1))
        result = self.room_1.join(self.normal_2)
        self.assertJoined(result, self.normal_2, self.room_1)

    def test_room_cannot_be_joined_if_its_full(self):
        self.room_2.join(self.normal_1, expiration=timedelta(-1))
        result = self.room_2.join(self.normal_2)
        self.assertError(result)

    def test_user_can_join_another_room(self):
        self.room_1.join(self.normal_1)
        result = self.room_2.join(self.normal_1)
        self.assertJoined(result, self.normal_1, self.room_2)

    def test_room_is_left_after_joining_other(self):
        self.room_1.join(self.normal_1)
        result = self.room_2.join(self.normal_1)
        self.assertEqual(self.room_1.userroom_set.count(), 0)

    def test_room_is_unlocked_after_joining_other(self):
        self.room_1.join(self.normal_1)
        self.room_2.join(self.normal_1)
        self.refresh()
        self.assertUnlocked(self.room_1)

    def test_room_is_not_unlocked_after_joining_other_by_not_owner(self):
        self.room_1.join(self.normal_1)
        result = self.room_1.join(self.normal_2, password=self.room_1.lock.password)
        self.assertJoined(result, self.normal_2, self.room_1)
        self.room_2.join(self.normal_2)
        self.refresh()
        self.assertLocked(self.room_1)
