# -*- coding: utf-8 -*-
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from users.models import Organization, User


class UserSerializer(ModelSerializer):
    date_joined = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "is_active", "is_staff", "date_joined")


class UserDataSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name")


class OrganizationSerializer(ModelSerializer):
    user = UserDataSerializer(read_only=True)
    accepted = serializers.BooleanField(read_only=True)

    class Meta:
        model = Organization
        fields = ("id", "name", "user", "accepted")
