# -*- coding: utf-8 -*-
from rooms.models import Room


def new_room(number, capacity=0, commit=True, **override):
    defaults = {'name': str(number), 'beds_single': capacity, 'available_beds_single': capacity}
    defaults.update(**override)
    room = Room(**defaults)

    if commit:
        room.save()

    return room
