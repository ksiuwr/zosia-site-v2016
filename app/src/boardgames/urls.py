from django.urls import re_path

from boardgames import views

urlpatterns = [
    re_path(r'^$', views.index, name='boardgames_index'),
    re_path(r'^my/$', views.my_boardgames, name='my_boardgames'),
    re_path(r'^my/delete/$', views.boardgame_delete, name='boardgames_delete'),
    re_path(r'^create/$', views.create, name='boardgames_create'),
    re_path(r'^vote/$', views.vote, name='boardgames_vote'),
    re_path(r'^vote/edit/$', views.vote_edit, name='vote_edit'),
    re_path(r'^accept/$', views.accept, name='boardgames_accept'),
    re_path(r'^accept/edit/$', views.accept_edit, name='accept_edit')
]
