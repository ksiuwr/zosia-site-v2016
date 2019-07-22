# -*- coding: utf-8 -*-
from rest_framework import serializers

from users.models import User
from ..models import Room, RoomBeds, RoomLock


# class RoomingUserSerializer(serializers.HyperlinkedModelSerializer):
class RoomingUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ("url", "first_name", "last_name")
        fields = ("id", "first_name", "last_name")


class RoomMemberSerializer(serializers.BaseSerializer):
    user = RoomingUserSerializer()
    joined_at = serializers.DateTimeField(input_formats=['iso-8601'])

    def to_representation(self, instance):
        return {"user": instance.user, "joined_at": instance.joined_at}

    def to_internal_value(self, data):
        user = data.get("user")
        joined_at = data.get("joined_at")

        if not user:
            raise serializers.ValidationError({"user": "This field is required."})

        if not joined_at:
            raise serializers.ValidationError({"joined_at": "This field is required."})

        user_serializer = RoomingUserSerializer(user)

        if not user_serializer.is_valid():
            raise serializers.ValidationError(user_serializer.errors)

        return {"user": user, "joined_at": joined_at}


class RoomLockSerializer(serializers.ModelSerializer):
    user = RoomMemberSerializer()

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
    members = RoomMemberSerializer(read_only=True, many=True)

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
    user = RoomingUserSerializer()

    def to_representation(self, instance):
        return {"user": instance.user}

    def to_internal_value(self, data):
        user = data.get("user")

        if not user:
            raise serializers.ValidationError({"user": "This field is required."})

        user_serializer = RoomingUserSerializer(user)

        if not user_serializer.is_valid():
            raise serializers.ValidationError(user_serializer.errors)

        return {"user": user}


class JoinMethodSerializer(serializers.BaseSerializer):
    user = RoomingUserSerializer()
    password = serializers.CharField(max_length=4)  # optional

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

        user_serializer = RoomingUserSerializer(user)

        if not user_serializer.is_valid():
            raise serializers.ValidationError(user_serializer.errors)

        return {"user": user, "password": password}


class LockMethodSerializer(serializers.BaseSerializer):
    user = RoomingUserSerializer()
    expiration_time = \
        serializers.DateTimeField(input_formats=['iso-8601'])  # only for admin, optional

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

        user_serializer = RoomingUserSerializer(user)

        if not user_serializer.is_valid():
            raise serializers.ValidationError(user_serializer.errors)

        return {"user": user, "expiration_time": expiration_time}


class UnlockMethodSerializer(serializers.BaseSerializer):
    user = RoomingUserSerializer()

    def to_representation(self, instance):
        return {"user": instance.user}

    def to_internal_value(self, data):
        user = data.get("user")

        if not user:
            raise serializers.ValidationError({"user": "This field is required."})

        user_serializer = RoomingUserSerializer(user)

        if not user_serializer.is_valid():
            raise serializers.ValidationError(user_serializer.errors)

        return {"user": user}
