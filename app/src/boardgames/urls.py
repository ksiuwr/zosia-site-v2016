from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='boardgames_index'),
    re_path(r'^create/$', views.create, name='boardgames_create'),
    re_path(r'^vote/$', views.vote, name='boardgames_vote'),
    re_path(r'^accept/$', views.accept, name='boardgames_accept')
]
