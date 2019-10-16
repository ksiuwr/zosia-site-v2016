# -*- coding: utf-8 -*-
from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadAuthenticatedWriteAdmin(BasePermission):
    def has_permission(self, request, view):
        sender = request.user

        return sender.is_authenticated and (request.method in SAFE_METHODS or sender.is_staff)
