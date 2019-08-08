# -*- coding: utf-8 -*-
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = format_suffix_patterns([
    path("", views.RoomList.as_view(), name="room-list"),
    path("<int:pk>/", views.RoomDetail.as_view(), name="room-detail"),
    path("<int:pk>/join/", views.join, name="room-join"),
    path("<int:pk>/leave/", views.leave, name="room-leave"),
    path("<int:pk>/lock/", views.lock, name="room-lock"),
    path("<int:pk>/unlock/", views.unlock, name="room-lock"),
    path("<int:pk>/hide/", views.hide, name="room-hide"),
    path("<int:pk>/unhide/", views.unhide, name="room-unhide"),
    path("members/", views.RoomMembersList.as_view(), name="room-members"),
])
