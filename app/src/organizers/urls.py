from django.urls import re_path

from organizers import views

urlpatterns = [
    re_path(r'^$', views.index, name='organizers_index'),
    re_path(r'^create$', views.update, name='organizers_add'),
    re_path(r'^(?P<contact_id>\d+)/$', views.update, name='organizers_edit'),
    re_path(r'^(?P<contact_id>\d+)/delete/$', views.delete, name='organizers_delete'),
]
