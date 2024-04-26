# -*- coding: utf-8 -*-
from django.urls import path

from rooms.api.v2 import views

urlpatterns = [
    path("", views.RoomViewSet.as_view(actions={"get": "list", "post": "create"}),
         name="rooms_api2_list"),
    path("<int:pk>/", views.RoomViewSet.as_view(actions={"get": "retrieve",
                                                         "put": "partial_update",
                                                         "delete": "destroy"}),
         name="rooms_api2_detail"),
    path("mine/", views.RoomViewSet.as_view(actions={"get": "user_member"}),
         name="rooms_api2_mine"),
    path("<int:pk>/hidden/",
         views.RoomViewSet.as_view(actions={"post": "hide", "delete": "unhide"}),
         name="rooms_api2_hidden"),
    path("<int:pk>/lock/", views.RoomLockViewSet.as_view(actions={"post": "create",
                                                                  "delete": "destroy"}),
         name="rooms_api2_lock"),
    path("<int:pk>/member/", views.RoomMemberViewSet.as_view(actions={"post": "create",
                                                                      "delete": "destroy"}),
         name="rooms_api2_member"),
    path("members/", views.UserRoomViewSet.as_view(actions={"get": "list"}),
         name="rooms_api2_all_members"),
]
