# -*- coding: utf-8 -*-
from rest_framework import serializers

from users.models import User
from ..models import Room, RoomBeds, RoomLock, UserRoom


# class MemberUserSerializer(serializers.HyperlinkedModelSerializer):
class MemberUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ("url", "first_name", "last_name")
        fields = ("id", "first_name", "last_name")


class UserRoomSerializer(serializers.ModelSerializer):
    user = MemberUserSerializer()
    joined_at = serializers.DateTimeField(input_formats=['iso-8601'])

    class Meta:
        model = UserRoom
        fields = ("user", "joined_at")


class RoomLockSerializer(serializers.ModelSerializer):
    user = UserRoomSerializer()

    class Meta:
        model = RoomLock
        fields = ("user", "password", "expiration_date")


class RoomBedsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomBeds
        fields = ("single", "double")


# class RoomSerializer(serializers.HyperlinkedModelSerializer):
class RoomSerializer(serializers.ModelSerializer):
    beds = RoomBedsSerializer()
    available_beds = RoomBedsSerializer()
    lock = RoomLockSerializer(read_only=True)
    members = UserRoomSerializer(read_only=True, many=True)

    class Meta:
        model = Room
        # fields = ("url", "name", "description", "hidden", "beds", "available_beds", "lock",
        fields = ("id", "name", "description", "hidden", "beds", "available_beds", "lock",
                  "members")

    def create(self, validated_data):
        beds_data = validated_data.pop("beds")
        available_beds_data = validated_data.pop("available_beds")
        beds_object = RoomBeds.objects.create(**beds_data)
        available_beds_object = RoomBeds.objects.create(**available_beds_data)

        return Room.objects.create(**validated_data, beds=beds_object,
                                   available_beds=available_beds_object)


class LeaveMethodSerializer(serializers.BaseSerializer):
    user = MemberUserSerializer()

    def to_representation(self, instance):
        return {"user": instance.user}

    def to_internal_value(self, data):
        user = data.get("user")

        if not user:
            raise serializers.ValidationError({"user": "This field is required."})

        user_serializer = MemberUserSerializer(user)

        if not user_serializer.is_valid():
            raise serializers.ValidationError(user_serializer.errors)

        return {"user": user}


class JoinMethodSerializer(serializers.BaseSerializer):
    user = MemberUserSerializer()
    password = serializers.CharField(max_length=4, required=False)  # optional

    def to_representation(self, instance):
        representation = {"user": instance.user}

        if instance.password:
            representation["password"] = instance.password

        return representation

    def to_internal_value(self, data):
        user = data.get("user")
        password = data.get("password")

        if not user:
            raise serializers.ValidationError({"user": "This field is required."})

        user_serializer = MemberUserSerializer(user)

        if not user_serializer.is_valid():
            raise serializers.ValidationError(user_serializer.errors)

        return {"user": user, "password": password}


class LockMethodSerializer(serializers.BaseSerializer):
    user = MemberUserSerializer()
    expiration_time = serializers.DateTimeField(input_formats=['iso-8601'],
                                                required=False)  # only for admin, optional

    def to_representation(self, instance):
        representation = {"user": instance.user}

        if instance.expiration_time:
            representation["expiration_time"] = instance.expiration_time

        return representation

    def to_internal_value(self, data):
        user = data.get("user")
        expiration_time = data.get("expiration_time")

        if not user:
            raise serializers.ValidationError({"user": "This field is required."})

        user_serializer = MemberUserSerializer(user)

        if not user_serializer.is_valid():
            raise serializers.ValidationError(user_serializer.errors)

        return {"user": user, "expiration_time": expiration_time}


class UnlockMethodSerializer(serializers.BaseSerializer):
    user = MemberUserSerializer()

    def to_representation(self, instance):
        return {"user": instance.user}

    def to_internal_value(self, data):
        user = data.get("user")

        if not user:
            raise serializers.ValidationError({"user": "This field is required."})

        user_serializer = MemberUserSerializer(user)

        if not user_serializer.is_valid():
            raise serializers.ValidationError(user_serializer.errors)

        return {"user": user}
