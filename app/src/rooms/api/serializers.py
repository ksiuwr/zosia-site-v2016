# -*- coding: utf-8 -*-
from rest_framework import serializers

from rooms.models import Room, RoomLock, UserRoom
from users.models import User
from utils.time_manager import TimeManager


class UserRoomSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects)

    class Meta:
        model = UserRoom
        fields = ("user", "joined_at")


class RoomMembersSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name")
    user_first_name = serializers.CharField(source="user.first_name")
    user_last_name = serializers.CharField(source="user.last_name")

    class Meta:
        model = UserRoom
        fields = ("room_name", "user_first_name", "user_last_name")


class RoomLockSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects)

    class Meta:
        model = RoomLock
        fields = ("user", "password", "expiration_date")


class RoomBedsSerializer(serializers.BaseSerializer):
    single = serializers.IntegerField()
    double = serializers.IntegerField()

    def to_representation(self, instance):
        return {"single": instance.get("single"), "double": instance.get("double")}

    def to_internal_value(self, data):
        single = data.get("single")
        double = data.get("double")

        return {"single": single, "double": double}


class RoomSerializer(serializers.ModelSerializer):
    # Accepted beds number range is from 0 to 42. You don't expect 43 beds in one room, do you?
    beds = serializers.DictField(child=serializers.IntegerField(min_value=0, max_value=42))
    available_beds = serializers.DictField(
        child=serializers.IntegerField(min_value=0, max_value=42))
    lock = RoomLockSerializer(read_only=True)
    members = UserRoomSerializer(source="userroom_set", read_only=True, many=True)

    class Meta:
        model = Room
        fields = ("id", "name", "description", "hidden", "beds", "available_beds", "lock",
                  "members")

    def create(self, validated_data):
        beds_data = validated_data.pop("beds")
        available_beds_data = validated_data.pop("available_beds")

        self._validate_beds(beds_data, available_beds_data)

        return Room.objects.create(**validated_data,
                                   beds_single=beds_data.get("single"),
                                   beds_double=beds_data.get("double"),
                                   available_beds_single=available_beds_data.get("single"),
                                   available_beds_double=available_beds_data.get("double"))

    def update(self, instance, validated_data):
        beds_data = validated_data.pop("beds")
        available_beds_data = validated_data.pop("available_beds")

        self._validate_beds(beds_data, available_beds_data)

        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.hidden = validated_data.get("hidden", instance.hidden)
        instance.beds_single = beds_data.get("single", instance.beds_single)
        instance.beds_double = beds_data.get("double", instance.beds_double)
        instance.available_beds_single = available_beds_data.get("single",
                                                                 instance.available_beds_single)
        instance.available_beds_double = available_beds_data.get("double",
                                                                 instance.available_beds_double)

        instance.save()

        return instance

    @staticmethod
    def _validate_beds(beds_data, available_beds_data):
        if available_beds_data.get("single") > beds_data.get("single"):
            raise serializers.ValidationError(
                "Cannot set more available single beds than real single beds")

        if available_beds_data.get("double") > beds_data.get("double"):
            raise serializers.ValidationError(
                "Cannot set more available double beds than real double beds")


class LeaveMethodSerializer(serializers.BaseSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects)

    def __init__(self, *args, **kwargs):
        super(LeaveMethodSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        return {"user": instance.user}

    def to_internal_value(self, data):
        user = data.get("user")

        if not user:
            raise serializers.ValidationError({"user": "This field is required."})

        return {"user": user}


class JoinMethodSerializer(serializers.BaseSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects)
    password = serializers.CharField(max_length=4, required=False)

    def __init__(self, *args, **kwargs):
        super(JoinMethodSerializer, self).__init__(*args, **kwargs)

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

        return {"user": user, "password": password}


class LockMethodSerializer(serializers.BaseSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects)

    def __init__(self, *args, **kwargs):
        super(LockMethodSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        return {"user": instance.user}

    def to_internal_value(self, data):
        user = data.get("user")

        if not user:
            raise serializers.ValidationError({"user": "This field is required."})

        return {"user": user}


class LockMethodAdminSerializer(serializers.BaseSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects)
    expiration_date = serializers.DateTimeField(input_formats=['iso-8601'],
                                                required=False)  # only for admin

    def __init__(self, *args, **kwargs):
        super(LockMethodAdminSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        representation = {"user": instance.user}

        if instance.expiration_date:
            representation["expiration_date"] = instance.expiration_date

        return representation

    def to_internal_value(self, data):
        user = data.get("user")
        expiration_date = data.get("expiration_date")

        if not user:
            raise serializers.ValidationError({"user": "This field is required."})

        return {"user": user} if not expiration_date else \
            {"user": user, "expiration_date": TimeManager.parse_timezone(expiration_date)}
