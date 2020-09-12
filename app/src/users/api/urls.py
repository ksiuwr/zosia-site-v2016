# -*- coding: utf-8 -*-
from django.urls import path

from users.api import views

urlpatterns = [
    path("", views.UserViewSet.as_view(actions={"get": "list"}), name="users_api_list"),
    path("<int:pk>/", views.UserViewSet.as_view(actions={"get": "retrieve"}),
         name="users_api_detail"),
    path("me/", views.UserViewSet.as_view(actions={"get": "session"}), name="users_api_me"),
    path("organizations/", views.OrganizationAPIView.as_view(), name="organizations_api_list")
]
