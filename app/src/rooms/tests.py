from django.core.exceptions import ValidationError
from django.test import TestCase

from rooms.test_helpers import RoomAssertions, create_room
from utils.test_helpers import create_user
from utils.time_manager import timedelta_since_now

room_assertions = RoomAssertions()


class RoomTestCase(TestCase):
    def refresh(self):
        self.room_1.refresh_from_db()
        self.room_2.refresh_from_db()

    def setUp(self):
        super().setUp()
        self.normal_1 = create_user(0)
        self.normal_2 = create_user(1)
        self.staff_1 = create_user(2, is_staff=True)
        self.staff_2 = create_user(3, is_staff=True)

        self.room_1 = create_room(111, capacity=2)
        self.room_2 = create_room(222, capacity=1)
        self.room_3 = create_room(333, capacity=3, hidden=True)

    # region join & leave

    def test_user_can_join_free_room(self):
        self.room_1.join(self.normal_1)
        room_assertions.assertJoined(self.normal_1, self.room_1)
        room_assertions.assertUnlocked(self.room_1)

    def test_user_cannot_join_locked_room_without_password(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        room_assertions.assertLocked(self.room_1, self.normal_1)

        with self.assertRaises(ValidationError):
            self.room_1.join(self.normal_2)

    def test_staff_cannot_join_locked_room_without_password(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        room_assertions.assertLocked(self.room_1, self.normal_1)

        with self.assertRaises(ValidationError):
            self.room_1.join(self.staff_2)

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

    def test_user_can_leave_locked_room(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        room_assertions.assertLocked(self.room_1, self.normal_1)

        self.room_1.leave(self.normal_1)
        self.assertEqual(self.room_1.members_count, 0)
        room_assertions.assertUnlocked(self.room_1)

    def test_staff_can_leave_locked_room(self):
        self.room_1.join(self.staff_2)
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        room_assertions.assertLocked(self.room_1, self.normal_1)

        self.room_1.leave(self.staff_2)
        self.assertEqual(self.room_1.members_count, 1)
        room_assertions.assertLocked(self.room_1, self.normal_1)

    def test_staff_can_remove_user_from_room(self):
        self.room_1.join(self.normal_1)
        self.room_1.leave(self.normal_1, self.staff_2)
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

    def test_user_cannot_add_other_user_room(self):
        with self.assertRaises(ValidationError):
            self.room_1.join(self.normal_1, self.normal_2)

    def test_user_cannot_remove_other_user_room(self):
        with self.assertRaises(ValidationError):
            self.room_1.leave(self.normal_1, self.normal_2)

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
                             expiration_date=timedelta_since_now(days=-30))
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
                             expiration_date=timedelta_since_now(days=7))
        self.refresh()
        room_assertions.assertLocked(self.room_1, self.normal_1)

    def test_staff_can_unlock_room_by_API(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        room_assertions.assertLocked(self.room_1, self.normal_1)

        self.room_1.unlock(self.staff_1, False)
        room_assertions.assertUnlocked(self.room_1)

    def test_staff_cannot_unlock_room_by_leaving(self):
        self.room_1.join(self.normal_1)
        self.room_1.set_lock(self.normal_1)
        room_assertions.assertLocked(self.room_1, self.normal_1)

        with self.assertRaises(ValidationError):
            self.room_1.unlock(self.staff_1, True)

    def test_staff_can_lock_hidden_room(self):
        self.room_3.join(self.normal_1, self.staff_1)
        self.room_3.set_lock(self.normal_1, self.staff_1)
        room_assertions.assertLocked(self.room_3, self.normal_1)

    # endregion
