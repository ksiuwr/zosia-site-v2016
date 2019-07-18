# -*- coding: utf-8 -*-
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from conferences.models import Zosia
from users.models import User
from .serializers import LeaveMethodSerializer, RoomSerializer
from ..models import Room


def get_room_or_404(*args, **kwargs):
    room = Room.objects.all_for_active_zosia(*args, **kwargs)

    if not room:
        raise Http404()


class RoomListAPI(APIView):
    def get(self, request, format=None):
        rooms = get_room_or_404()
        serializer = RoomSerializer(rooms, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        zosia = Zosia.objects.find_active()

        if not zosia:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = RoomSerializer(data=request.data, zosia=zosia.id)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomDetailsAPI(APIView):
    def get(self, request, pk, format=None):
        room = get_room_or_404(pk=pk)
        serializer = RoomSerializer(room)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        room = get_room_or_404(pk=pk)
        serializer = RoomSerializer(room, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        room = get_room_or_404(pk=pk)
        room.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def leave(request, pk, format=None):
    # user data taken from session
    room = get_room_or_404(pk=pk)
    serializer = LeaveMethodSerializer(data=request.data)

    if serializer.is_valid():
        user_data = serializer.validated_data.user
        user = get_object_or_404(User, pk=user_data.id)
        room.members.remove(user)

        return Response(status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def join(request, pk, format=None):  # only room joining
    room = get_room_or_404(pk=pk)


@api_view(["POST"])
def lock(request, pk, format=None):  # only locks the room
    room = get_room_or_404(pk=pk)


@api_view(["POST"])
def unlock(request, pk, format=None):
    room = get_room_or_404(pk=pk)


@api_view(["POST"])
def hide(request, pk, format=None):
    room = get_room_or_404(pk=pk)
    room.hidden = True
    room.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def unhide(request, pk, format=None):
    room = get_room_or_404(pk=pk)
    room.hidden = False
    room.save()

    return Response(status=status.HTTP_200_OK)
