# -*- coding: utf-8 -*-
from django.core import exceptions
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, ViewSet

from conferences.models import Zosia
from rooms.api.v2.serializers import RoomLockCreateMethodAdminSerializer, \
    RoomLockCreateMethodSerializer, RoomMemberCreateMethodSerializer, \
    RoomMemberDestroyMethodSerializer, RoomSerializer, RoomWithLockPasswordSerializer, \
    UserRoomSerializer
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
            raise exceptions.ValidationError(_("Rooming for user has not started yet."),
                                             code='invalid')

        if rooming_status == RoomingStatus.AFTER_ROOMING:
            raise exceptions.ValidationError(_("Rooming has already ended."), code='invalid')

        if rooming_status == RoomingStatus.ROOMING_UNAVAILABLE:
            raise exceptions.ValidationError(_("Rooming is unavailable for user."), code='invalid')


class UserRoomViewSet(ReadOnlyModelViewSet):
    queryset = UserRoom.objects.all()
    serializer_class = UserRoomSerializer
    permission_classes = [IsAdminUser]


class RoomViewSet(ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [ReadAuthenticatedWriteAdmin]

    def get_queryset(self):
        sender = self.request.user

        return Room.objects.all() if sender.is_staff else \
            Room.objects.all_visible_with_member(sender)

    @action(detail=True, methods=["POST"])
    def hide(self, request, pk):
        room = self.get_object()
        room.hidden = True
        room.save()

        return Response(self.get_serializer(room).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["DELETE"])
    def unhide(self, request, pk):
        room = self.get_object()
        room.hidden = False
        room.save()

        return Response(self.get_serializer(room).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"])
    def user_member(self, request):
        sender = request.user
        room = sender.room_of_user.all().first()

        if not room:
            return Response("User is not assigned to any room", status=status.HTTP_404_NOT_FOUND)

        return Response(self.get_serializer(room).data, status=status.HTTP_200_OK)


class RoomMemberViewSet(ViewSet):
    def create(self, request, pk):  # only room joining
        room = get_object_or_404(Room, pk=pk)
        sender = request.user
        serializer = RoomMemberCreateMethodSerializer(data=request.data)

        if serializer.is_valid():
            user_id = serializer.validated_data.get("user")
            password = serializer.validated_data.get("password")
            user = User.objects.filter(pk=user_id).first()

            if not user:
                return Response(_("Specified user does not exist."),
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                _check_rooming(user, sender)
                room.join(user, sender, password)
            except exceptions.ValidationError as e:
                return Response("; ".join(e.messages), status=status.HTTP_403_FORBIDDEN)

            return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        sender = request.user
        serializer = RoomMemberDestroyMethodSerializer(data=request.data)

        if serializer.is_valid():
            user_id = serializer.validated_data.get("user")
            user = User.objects.filter(pk=user_id).first()

            if not user:
                return Response(_("Specified user does not exist."),
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                _check_rooming(user, sender)
                room.leave(user, sender)
            except exceptions.ValidationError as e:
                return Response("; ".join(e.messages), status=status.HTTP_403_FORBIDDEN)

            return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomLockViewSet(ViewSet):
    def create(self, request, pk):  # only locks the room
        room = get_object_or_404(Room, pk=pk)
        sender = request.user
        serializer = RoomLockCreateMethodAdminSerializer(data=request.data) \
            if sender.is_staff else RoomLockCreateMethodSerializer(data=request.data)

        if serializer.is_valid():
            user_id = serializer.validated_data.get("user")
            expiration_date = serializer.validated_data.get("expiration_date")
            user = User.objects.filter(pk=user_id).first()

            if not user:
                return Response(_("Specified user does not exist."),
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                _check_rooming(user, sender)
                room.set_lock(user, sender, expiration_date)
            except exceptions.ValidationError as e:
                return Response('; '.join(e.messages), status=status.HTTP_403_FORBIDDEN)

            return Response(RoomWithLockPasswordSerializer(room).data,
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        sender = request.user

        try:
            _check_rooming(sender, sender)
            room.unlock(sender)
        except exceptions.ValidationError as e:
            return Response('; '.join(e.messages), status=status.HTTP_403_FORBIDDEN)

        return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
