from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='rooms_index'),
    url(r'^status/$', views.status, name='rooms_status'),
    url(r'^(?P<room_id>\d+)/join/$', views.join, name='rooms_join'),
    url(r'^unlock/$', views.unlock, name='rooms_unlock'),
]
