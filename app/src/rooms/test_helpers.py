# -*- coding: utf-8 -*-
from unittest import TestCase

from rooms.models import Room


def new_room(number, capacity=0, commit=True, **override):
    defaults = {'name': str(number), 'beds_single': capacity, 'available_beds_single': capacity}
    defaults.update(**override)
    room = Room(**defaults)

    if commit:
        room.save()

    return room


class RoomAssertions(TestCase):
    def assertEmpty(self, room):
        self.assertEqual(room.members_count, 0)

    def assertJoined(self, user, room):
        self.assertIn(user, room.members.all())

    def assertLocked(self, room, user):
        self.assertTrue(room.is_locked)
        self.assertTrue(room.lock.is_owned_by(user))

    def assertUnlocked(self, room):
        self.assertFalse(room.is_locked)

    def assertHidden(self, room):
        self.assertTrue(room.hidden)

    def assertUnhidden(self, room):
        self.assertFalse(room.hidden)
