from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='sponsors_index'),
    re_path(r'^create$', views.update, name='sponsors_add'),
    re_path(r'^(?P<sponsor_id>\d+)/$', views.update, name='sponsors_edit'),
    re_path(r'^toggle_active/$', views.toggle_active, name='sponsors_toggle_active'),
]
