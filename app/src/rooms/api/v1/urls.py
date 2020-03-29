# -*- coding: utf-8 -*-
from django.urls import path

from rooms.api.v1 import views

urlpatterns = [
        path("", views.RoomViewSet.as_view({"get": "list", "post": "create"}),
             name="rooms_api_list"),
        path("<int:pk>/", views.RoomViewSet.as_view({"get": "retrieve",
                                                     "put": "partial_update",
                                                     "delete": "destroy"}),
             name="rooms_api_detail"),
        path("<int:pk>/join/", views.join, name="rooms_api_join"),
        path("<int:pk>/leave/", views.leave, name="rooms_api_leave"),
        path("<int:pk>/lock/", views.lock, name="rooms_api_lock"),
        path("<int:pk>/unlock/", views.unlock, name="rooms_api_unlock"),
        path("<int:pk>/hide/", views.RoomViewSet.as_view({"post": "hide"}), name="rooms_api_hide"),
        path("<int:pk>/unhide/", views.RoomViewSet.as_view({"post": "unhide"}),
             name="rooms_api_unhide"),
        path("members/", views.RoomMembersViewSet.as_view({"get": "list"}),
             name="rooms_api_members"),
]
