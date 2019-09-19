# -*- coding: utf-8 -*-
from django.core import exceptions
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from conferences.models import RoomingStatus, UserPreferences, Zosia
from rooms.api.serializers import JoinMethodSerializer, LeaveMethodSerializer, \
    LockMethodAdminSerializer, LockMethodSerializer, RoomMembersSerializer, RoomSerializer
from rooms.models import Room, UserRoom
from users.models import User


class RoomMembersList(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, version):
        user_room = UserRoom.objects.all()
        serializer = RoomMembersSerializer(user_room, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class RoomList(APIView):
    def get(self, request, version):
        sender = request.user
        rooms = Room.objects.all() if sender.is_staff else Room.objects.all_visible()
        serializer = RoomSerializer(rooms, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, version):
        if not request.user.is_staff:
            raise exceptions.PermissionDenied()

        serializer = RoomSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            instance = serializer.save()
            response_data = RoomSerializer(instance).data

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomDetail(APIView):
    def get(self, request, version, pk):
        room = get_object_or_404(Room, pk=pk)

        if not request.user.is_staff and room.hidden:
            raise exceptions.PermissionDenied()

        serializer = RoomSerializer(room, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, version, pk):
        if not request.user.is_staff:
            raise exceptions.PermissionDenied()

        room = get_object_or_404(Room, pk=pk)
        serializer = RoomSerializer(room, data=request.data, context={'request': request},
                                    partial=True)

        if serializer.is_valid():
            instance = serializer.save()
            response_data = RoomSerializer(instance).data

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, version, pk):
        if not request.user.is_staff:
            raise exceptions.PermissionDenied()

        room = get_object_or_404(Room, pk=pk)
        room.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


def check_rooming(user, sender):
    if not sender.is_staff:
        zosia = Zosia.objects.find_active_or_404()
        user_prefs = get_object_or_404(UserPreferences, zosia=zosia, user=user)
        rooming_status = zosia.get_rooming_status(user_prefs)

        if rooming_status == RoomingStatus.BEFORE_ROOMING:
            raise exceptions.ValidationError("Rooming for user has not started yet.")

        if rooming_status == RoomingStatus.AFTER_ROOMING:
            raise exceptions.ValidationError("Rooming has already ended.")

        if rooming_status == RoomingStatus.ROOMING_UNAVAILABLE:
            raise exceptions.ValidationError("Rooming is unavailable for user.")


@api_view(["POST"])
def leave(request, version, pk):
    room = get_object_or_404(Room, pk=pk)
    sender = request.user
    serializer = LeaveMethodSerializer(data=request.data)

    if serializer.is_valid():
        user_id = serializer.validated_data.get("user")
        user = get_object_or_404(User, pk=user_id)

        try:
            check_rooming(user, sender)
            room.leave(user, sender)
        except exceptions.ValidationError as e:
            return Response("; ".join(e.messages), status=status.HTTP_403_FORBIDDEN)

        return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def join(request, version, pk):  # only room joining
    room = get_object_or_404(Room, pk=pk)
    sender = request.user
    serializer = JoinMethodSerializer(data=request.data)

    if serializer.is_valid():
        user_id = serializer.validated_data.get("user")
        password = serializer.validated_data.get("password")
        user = get_object_or_404(User, pk=user_id)

        try:
            check_rooming(user, sender)
            room.join(user, sender, password)
        except exceptions.ValidationError as e:
            return Response("; ".join(e.messages), status=status.HTTP_403_FORBIDDEN)

        return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def lock(request, version, pk):  # only locks the room
    room = get_object_or_404(Room, pk=pk)
    sender = request.user
    serializer = LockMethodAdminSerializer(data=request.data) \
        if sender.is_staff else LockMethodSerializer(data=request.data)

    if serializer.is_valid():
        user_id = serializer.validated_data.get("user")
        expiration_date = serializer.validated_data.get("expiration_date")
        user = get_object_or_404(User, pk=user_id)

        try:
            check_rooming(user, sender)
            room.set_lock(user, sender, expiration_date)
        except exceptions.ValidationError as e:
            return Response('; '.join(e.messages), status=status.HTTP_403_FORBIDDEN)

        return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def unlock(request, version, pk):
    room = get_object_or_404(Room, pk=pk)
    sender = request.user

    try:
        check_rooming(sender, sender)
        room.unlock(sender)
    except exceptions.ValidationError as e:
        return Response('; '.join(e.messages), status=status.HTTP_403_FORBIDDEN)

    return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def hide(request, version, pk):
    room = get_object_or_404(Room, pk=pk)
    room.hidden = True
    room.save()

    return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def unhide(request, version, pk):
    room = get_object_or_404(Room, pk=pk)
    room.hidden = False
    room.save()

    return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
