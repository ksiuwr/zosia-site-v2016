# -*- coding: utf-8 -*-
from django.core import exceptions
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from .serializers import JoinMethodSerializer, LeaveMethodSerializer, LockMethodAdminSerializer, \
    LockMethodSerializer, RoomSerializer
from ..models import Room


class RoomList(APIView):
    def get(self, request, version, format=None):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, version, format=None):
        serializer = RoomSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomDetail(APIView):
    def get(self, request, version, pk, format=None):
        room = get_object_or_404(Room, pk=pk)
        serializer = RoomSerializer(room, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, version, pk, format=None):
        room = get_object_or_404(Room, pk=pk)
        serializer = RoomSerializer(room, data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, version, pk, format=None):
        room = get_object_or_404(Room, pk=pk)
        room.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def leave(request, version, pk, format=None):
    room = get_object_or_404(Room, pk=pk)
    serializer = LeaveMethodSerializer(data=request.data)

    if serializer.is_valid():
        user_id = serializer.validated_data.get("user")
        user = get_object_or_404(User, pk=user_id)
        room.leave(user)

        return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def join(request, version, pk, format=None):  # only room joining
    room = get_object_or_404(Room, pk=pk)
    serializer = JoinMethodSerializer(data=request.data)

    if serializer.is_valid():
        user_id = serializer.validated_data.get("user")
        user = get_object_or_404(User, pk=user_id)

        try:
            room.join(user)
        except exceptions.ValidationError as e:
            return Response({"status": e.message}, status=status.HTTP_403_FORBIDDEN)

        return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def lock(request, version, pk, format=None):  # only locks the room
    room = get_object_or_404(Room, pk=pk)
    locker = request.user
    serializer = LockMethodAdminSerializer(data=request.data) \
        if locker.is_staff or locker.is_superuser else \
        LockMethodSerializer(data=request.data)

    if serializer.is_valid():
        user_id = serializer.validated_data.get("user")
        expiration_date = serializer.validated_data.get("expiration_date")
        user = get_object_or_404(User, pk=user_id)

        try:
            room.set_lock(user, locker, expiration_date)
        except exceptions.ValidationError as e:
            return Response('; '.join(e.messages), status=status.HTTP_403_FORBIDDEN)

        return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def unlock(request, version, pk, format=None):
    room = get_object_or_404(Room, pk=pk)
    user = request.user

    try:
        room.unlock(user)
    except exceptions.ValidationError as e:
        return Response('; '.join(e.messages), status=status.HTTP_403_FORBIDDEN)

    return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def hide(request, version, pk, format=None):
    room = get_object_or_404(Room, pk=pk)
    room.hidden = True
    room.save()

    return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def unhide(request, version, pk, format=None):
    room = get_object_or_404(Room, pk=pk)
    room.hidden = False
    room.save()

    return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
