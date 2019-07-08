from django.forms.models import model_to_dict
from django.shortcuts import reverse
from rest_framework import serializers

from rooms.models import Room, RoomBeds, RoomLock


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


class RoomLockSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomLock
        fields = ('user', 'expiration_date')


class RoomBedsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomBeds
        fields = ('single', 'double', 'other')


class RoomSerializer(serializers.ModelSerializer):
    beds = RoomBedsSerializer()
    available_beds = RoomBedsSerializer()
    lock = RoomLockSerializer(read_only=True)
    users = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = Room
        fields = ('id', 'name', 'hidden', 'beds', 'available_beds', 'lock', 'users')

    def create(self, validated_data):
        beds_data = validated_data.pop('beds')
        available_beds_data = validated_data.pop('available_beds')
        beds_object = RoomBeds.objects.create(**beds_data)
        available_beds_object = RoomBeds.objects.create(**available_beds_data)
        room = Room.objects.create(**validated_data, beds=beds_object,
                                   available_beds=available_beds_object)

        return room
