# -*- coding: utf-8 -*-
from conferences.models import Zosia
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RoomSerializer
from ..models import Room


def get_room_by_id(id):
    zosia = get_object_or_404(Zosia, active=True)
    return get_object_or_404(Room, zosia=zosia, pk=id)


class RoomListAPI(APIView):
    def get(self, request, format=None):
        zosia = get_object_or_404(Zosia, active=True)
        rooms = Room.objects.for_zosia(zosia)
        serializer = RoomSerializer(rooms, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = RoomSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomDetailsAPI(APIView):
    def get(self, request, id, format=None):
        room = get_room_by_id(id)
        serializer = RoomSerializer(room)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id, format=None):
        room = get_room_by_id(id)
        serializer = RoomSerializer(room, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        room = get_room_by_id(id)
        room.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
