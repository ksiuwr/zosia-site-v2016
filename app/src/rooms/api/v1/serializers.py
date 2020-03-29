# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from rooms.models import Room, RoomLock, UserRoom
from users.api.serializers import UserDataSerializer
from users.models import User
from utils.time_manager import parse_timezone


class UserInRoomSerializer(serializers.ModelSerializer):
    user = UserDataSerializer()

    class Meta:
        model = UserRoom
        fields = ("user", "joined_at")


class RoomMembersSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name")
    user = UserDataSerializer()

    class Meta:
        model = UserRoom
        fields = ("room_name", "user")


class RoomLockSerializer(serializers.ModelSerializer):
    user = UserDataSerializer()
    password = serializers.SerializerMethodField("send_password")

    class Meta:
        model = RoomLock
        fields = ("user", "password", "expiration_date")

    def send_password(self, obj):
        request = self.context.get("request")

        return obj.password if request and obj.user == request.user else None


class RoomLockWithPasswordSerializer(serializers.ModelSerializer):
    user = UserDataSerializer()

    class Meta:
        model = RoomLock
        fields = ("user", "password", "expiration_date")


class RoomSerializer(serializers.ModelSerializer):
    # Accepted beds number range is from 0 to 42. You don't expect 43 beds in one room, do you?
    beds_single = serializers.IntegerField(min_value=0, max_value=42)
    beds_double = serializers.IntegerField(min_value=0, max_value=42)
    available_beds_single = serializers.IntegerField(min_value=0, max_value=42)
    available_beds_double = serializers.IntegerField(min_value=0, max_value=42)
    lock = RoomLockSerializer(read_only=True)
    members = UserInRoomSerializer(source="userroom_set", read_only=True, many=True)

    class Meta:
        model = Room
        fields = ("id", "name", "description", "hidden", "beds_single", "beds_double",
                  "available_beds_single", "available_beds_double", "lock", "members")

    def validate(self, data):
        super().validate(data)

        beds_single_data = data.get("beds_single",
                                    0 if self.instance is None else self.instance.beds_single)
        beds_double_data = data.get("beds_double",
                                    0 if self.instance is None else self.instance.beds_double)
        available_beds_single_data = data.get("available_beds_single",
                                              0 if self.instance is None
                                              else self.instance.available_beds_single)
        available_beds_double_data = data.get("available_beds_double",
                                              0 if self.instance is None
                                              else self.instance.available_beds_double)

        if available_beds_single_data > beds_single_data + beds_double_data:
            raise serializers.ValidationError(
                    _("Available single beds cannot exceed real single beds plus double beds"),
                    code='invalid'
            )

        double_as_single = max(0, available_beds_single_data - beds_single_data)

        if available_beds_double_data > beds_double_data - double_as_single:
            raise serializers.ValidationError(_(
                    "Available double beds cannot exceed real double beds minus double-as-single beds"),
                    code='invalid'
            )

        available_members = available_beds_single_data + 2 * available_beds_double_data
        members_count = 0 if self.instance is None else len(self.instance.members.all())

        if available_members < members_count:
            raise serializers.ValidationError(
                    _("Available beds must exceed already joined members"),
                    code='invalid'
            )

        return data


class RoomWithLockPasswordSerializer(RoomSerializer):
    lock = RoomLockWithPasswordSerializer(read_only=True)


class LeaveMethodSerializer(serializers.BaseSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects)

    def __init__(self, *args, **kwargs):
        super(LeaveMethodSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        return {"user": instance.user}

    def to_internal_value(self, data):
        user = data.get("user")

        if user is None:
            raise serializers.ValidationError({"user": "This field is required."}, code='required')

        return {"user": user}


class JoinMethodSerializer(serializers.BaseSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects)
    password = serializers.CharField(max_length=4, required=False)

    def __init__(self, *args, **kwargs):
        super(JoinMethodSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        representation = {"user": instance.user}

        if instance.password is not None:
            representation["password"] = instance.password

        return representation

    def to_internal_value(self, data):
        user = data.get("user")
        password = data.get("password")

        if user is None:
            raise serializers.ValidationError({"user": "This field is required."}, code='required')

        return {"user": user, "password": password}


class LockMethodSerializer(serializers.BaseSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects)

    def __init__(self, *args, **kwargs):
        super(LockMethodSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        return {"user": instance.user}

    def to_internal_value(self, data):
        user = data.get("user")

        if user is None:
            raise serializers.ValidationError({"user": "This field is required."}, code='required')

        return {"user": user}


class LockMethodAdminSerializer(serializers.BaseSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects)
    expiration_date = serializers.DateTimeField(input_formats=['iso-8601'], required=False)

    def __init__(self, *args, **kwargs):
        super(LockMethodAdminSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        representation = {"user": instance.user}

        if instance.expiration_date is not None:
            representation["expiration_date"] = instance.expiration_date

        return representation

    def to_internal_value(self, data):
        user = data.get("user")
        expiration_date = data.get("expiration_date")

        if user is None:
            raise serializers.ValidationError({"user": "This field is required."}, code='required')

        return {"user": user} if expiration_date is None else \
            {"user": user, "expiration_date": parse_timezone(expiration_date)}
