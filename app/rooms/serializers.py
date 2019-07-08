from django.forms.models import model_to_dict
from django.shortcuts import reverse
from rest_framework import serializers

from rooms.models import Room


def room_to_dict(room):
    model = model_to_dict(room)
    model['join'] = reverse('rooms_join', kwargs={'room_id': room.pk})
    model['capacity'] = room.capacity
    model['is_locked'] = room.is_locked
    model['free_places'] = room.capacity - room.users.count()
    model.pop('users')

    return model


def user_to_dict(user):
    name = user.display_name
    dic = {'name': name}

    return dic


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('id', 'name', 'hidden', 'beds', 'available_beds', 'lock', 'users')
