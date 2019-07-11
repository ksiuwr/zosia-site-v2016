# -*- coding: utf-8 -*-
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = format_suffix_patterns([
    path("", views.RoomListAPI.as_view(), name="all_rooms"),
    path("<int:id>/", views.RoomDetailsAPI.as_view(), name="single room"),
    path("<int:id>/leave/", views.leave, name="leave room"),
    path("<int:id>/join/", views.leave, name="leave room"),
    path("<int:id>/lock/", views.leave, name="leave room"),
])
