# -*- coding: utf-8 -*-
from django.core import exceptions
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from conferences.models import Zosia
from rooms.api.serializers import JoinMethodSerializer, LeaveMethodSerializer, \
    LockMethodAdminSerializer, LockMethodSerializer, RoomMembersSerializer, RoomSerializer, \
    RoomWithLockPasswordSerializer
from rooms.models import Room, UserRoom
from users.models import User, UserPreferences
from utils.api import ReadAuthenticatedWriteAdmin
from utils.constants import RoomingStatus


def _check_rooming(user, sender):
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


class RoomViewSet(ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [ReadAuthenticatedWriteAdmin]

    def get_queryset(self):
        sender = self.request.user

        return Room.objects.all() if sender.is_staff else Room.objects.all_visible()

    @action(detail=True, methods=["POST"])
    def hide(self, request, version, pk):
        room = self.get_object()
        room.hidden = True
        room.save()

        return Response(self.get_serializer(room).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def unhide(self, request, version, pk):
        room = self.get_object()
        room.hidden = False
        room.save()

        return Response(self.get_serializer(room).data, status=status.HTTP_200_OK)


@api_view(["POST"])
def join(request, version, pk):  # only room joining
    room = get_object_or_404(Room, pk=pk)
    sender = request.user
    serializer = JoinMethodSerializer(data=request.data)

    if serializer.is_valid():
        user_id = serializer.validated_data.get("user")
        password = serializer.validated_data.get("password")
        user = User.objects.filter(pk=user_id).first()

        if not user:
            return Response("Specified user does not exist.", status=status.HTTP_400_BAD_REQUEST)

        try:
            _check_rooming(user, sender)
            room.join(user, sender, password)
        except exceptions.ValidationError as e:
            return Response("; ".join(e.messages), status=status.HTTP_403_FORBIDDEN)

        return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def leave(request, version, pk):
    room = get_object_or_404(Room, pk=pk)
    sender = request.user
    serializer = LeaveMethodSerializer(data=request.data)

    if serializer.is_valid():
        user_id = serializer.validated_data.get("user")
        user = User.objects.filter(pk=user_id).first()

        if not user:
            return Response("Specified user does not exist.", status=status.HTTP_400_BAD_REQUEST)

        try:
            _check_rooming(user, sender)
            room.leave(user, sender)
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
        user = User.objects.filter(pk=user_id).first()

        if not user:
            return Response("Specified user does not exist.", status=status.HTTP_400_BAD_REQUEST)

        try:
            _check_rooming(user, sender)
            room.set_lock(user, sender, expiration_date)
        except exceptions.ValidationError as e:
            return Response('; '.join(e.messages), status=status.HTTP_403_FORBIDDEN)

        return Response(RoomWithLockPasswordSerializer(room).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def unlock(request, version, pk):
    room = get_object_or_404(Room, pk=pk)
    sender = request.user

    try:
        _check_rooming(sender, sender)
        room.unlock(sender)
    except exceptions.ValidationError as e:
        return Response('; '.join(e.messages), status=status.HTTP_403_FORBIDDEN)

    return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)


class RoomMembersViewSet(ReadOnlyModelViewSet):
    queryset = UserRoom.objects.all()
    serializer_class = RoomMembersSerializer
    permission_classes = [IsAdminUser]
