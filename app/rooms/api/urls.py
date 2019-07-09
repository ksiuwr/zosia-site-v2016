# -*- coding: utf-8 -*-
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = format_suffix_patterns([
    path('', views.RoomListAPI.as_view(), name='all_rooms'),
])
