from django.urls import re_path

from boardgames import views

urlpatterns = [
    re_path(r'^$', views.index, name='boardgames_index'),
    re_path(r'^my_boardgames/$', views.my_boardgames, name='my_boardgames'),
    re_path(r'^my_boardgames/delete/$',
            views.boardgame_delete, name='boardgames_delete'),
    re_path(r'^create/$', views.create, name='boardgames_create'),
    re_path(r'^vote/$', views.vote, name='boardgames_vote'),
    re_path(r'^vote/post/$', views.vote_edit, name='vote_edit'),
    re_path(r'^accept/$', views.accept, name='boardgames_accept'),
    re_path(r'^accept/post/$', views.accept_edit, name='accept_edit')
]
