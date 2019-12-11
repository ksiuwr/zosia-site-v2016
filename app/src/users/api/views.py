# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from users.api.serializers import UserSerializer
from users.models import User


class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.order_by("last_name", "first_name")
    serializer_class = UserSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated] if self.action == "session" else [IsAdminUser]

        return [permission() for permission in permission_classes]

    @action(detail=False, methods=["GET"])
    def session(self, request, version):
        sender = request.user
        serializer = self.get_serializer(sender)

        return Response(serializer.data, status=status.HTTP_200_OK)
