from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='boardgames_index'),
    url(r'^create$', views.create, name='boardgames_create'),
    url(r'^vote$', views.vote, name='boardgames_vote'),
]
