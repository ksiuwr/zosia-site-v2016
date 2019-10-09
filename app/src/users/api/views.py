# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from users.api.serializers import UserSerializer
from users.models import User


class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


@api_view(["GET"])
def session_user(request, version):
    sender = request.user
    serializer = UserSerializer(sender, context={'request': request})

    return Response(serializer.data, status=status.HTTP_200_OK)
