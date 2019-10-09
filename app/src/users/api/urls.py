# -*- coding: utf-8 -*-
from django.urls import path

from users.api import views

urlpatterns = [
    path("", views.UserViewSet.as_view({"get": "list"}), name="users_api_list"),
    path("<int:pk>/", views.UserViewSet.as_view({"get": "retrieve"}), name="users_api_detail"),
    path("me/", views.session_user, name="users_api_me")
]
