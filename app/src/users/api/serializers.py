# -*- coding: utf-8 -*-
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from users.models import User


class UserSerializer(ModelSerializer):
    date_joined = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "is_active", "is_staff", "date_joined")


class UserDataSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name")
