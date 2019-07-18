# -*- coding: utf-8 -*-
from rest_framework import serializers

from users.models import User
from ..models import Room, RoomBeds, RoomLock


class RoomingUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("url", "first_name", "last_name")


class RoomMemberSerializer(serializers.HyperlinkedModelSerializer):
    user = RoomingUserSerializer()
    joined_at = serializers.DateTimeField(input_formats=['iso-8601'])

    class Meta:
        model = User
        fields = ("user", "joined_at")


class RoomLockSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomLock
        fields = ("user", "password", "expiration_date")


class RoomBedsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomBeds
        fields = ("single", "double")


class RoomSerializer(serializers.HyperlinkedModelSerializer):
    beds = RoomBedsSerializer()
    available_beds = RoomBedsSerializer()
    lock = RoomLockSerializer(read_only=True)
    members = RoomingUserSerializer(read_only=True, many=True)
    zosia = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Room
        fields = ("url", "zosia", "name", "description", "hidden", "beds", "available_beds",
                  "lock", "members")

    def create(self, validated_data):
        beds_data = validated_data.pop("beds")
        available_beds_data = validated_data.pop("available_beds")
        beds_object = RoomBeds.objects.create(**beds_data)
        available_beds_object = RoomBeds.objects.create(**available_beds_data)

        return Room.objects.create(**validated_data, beds=beds_object,
                                   available_beds=available_beds_object)


class LeaveMethodSerializer(serializers.BaseSerializer):
    user = RoomingUserSerializer(read_only=True)


class JoinMethodSerializer(serializers.BaseSerializer):
    user = RoomingUserSerializer(read_only=True)
    password = serializers.CharField(max_length=300)  # optional


class LockMethodSerializer(serializers.BaseSerializer):
    user = RoomingUserSerializer(read_only=True)
    expiration_time = \
        serializers.DateTimeField(input_formats=['iso-8601'])  # only for admin, optional


class UnlockMethodSerializer(serializers.BaseSerializer):
    pass
