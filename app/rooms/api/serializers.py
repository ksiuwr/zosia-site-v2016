# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import Room, RoomBeds, RoomLock


class RoomLockSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomLock
        fields = ('user', 'expiration_date')


class RoomBedsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomBeds
        fields = ('single', 'double', 'other')


class RoomSerializer(serializers.ModelSerializer):
    zosia = serializers.PrimaryKeyRelatedField(read_only=True)
    beds = RoomBedsSerializer()
    available_beds = RoomBedsSerializer()
    lock = RoomLockSerializer(read_only=True)
    users = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = Room
        fields = ('id', 'zosia', 'name', 'hidden', 'beds', 'available_beds', 'lock', 'users')

    def create(self, validated_data):
        beds_data = validated_data.pop('beds')
        available_beds_data = validated_data.pop('available_beds')
        beds_object = RoomBeds.objects.create(**beds_data)
        available_beds_object = RoomBeds.objects.create(**available_beds_data)
        room = Room.objects.create(**validated_data, beds=beds_object,
                                   available_beds=available_beds_object)

        return room


class LockMethodSerializer(serializers.BaseSerializer):
    pass


class JoinMethodSerializer(serializers.BaseSerializer):
    pass
