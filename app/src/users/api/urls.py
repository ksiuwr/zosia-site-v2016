# -*- coding: utf-8 -*-
from django.urls import path

from users.api import views

urlpatterns = [
    path("", views.UserList.as_view(), name="users_api_list"),
    path("me/", views.session_user, name="users_api_me")
]
