# -*- coding: utf-8 -*-
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = format_suffix_patterns([
    path("", views.RoomListAPI.as_view(), name="all_rooms"),
    path("<int:pk>/", views.RoomDetailsAPI.as_view(), name="single room"),
    path("<int:pk>/leave/", views.leave, name="leave room"),
    path("<int:pk>/join/", views.leave, name="join room"),
    path("<int:pk>/lock/", views.leave, name="lock room"),
    path("<int:pk>/unlock/", views.leave, name="unlock room"),
    path("<int:pk>/hide/", views.leave, name="lock room"),
    path("<int:pk>/unhide/", views.leave, name="unlock room"),
])
