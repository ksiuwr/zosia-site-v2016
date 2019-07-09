# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RoomSerializer
from ..models import Room


class RoomListAPI(APIView):
    def get(self, request, format=None):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = RoomSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
