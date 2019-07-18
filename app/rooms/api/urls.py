# -*- coding: utf-8 -*-
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = format_suffix_patterns([
    path("", views.RoomListAPI.as_view(), name="all_rooms"),
    path("<int:id>/", views.RoomDetailsAPI.as_view(), name="single room"),
    path("<int:id>/leave/", views.leave, name="leave room"),
    path("<int:id>/join/", views.leave, name="join room"),
    path("<int:id>/lock/", views.leave, name="lock room"),
    path("<int:id>/unlock/", views.leave, name="unlock room"),
    path("<int:id>/hide/", views.leave, name="lock room"),
    path("<int:id>/unhide/", views.leave, name="unlock room"),
])
