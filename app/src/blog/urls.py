from django.urls import re_path

from blog import views

urlpatterns = [
    re_path(r'^$', views.index, name='blog_index'),
    re_path(r'^create$', views.create, name='blog_create'),
    re_path(r'^list$', views.list, name='blog_list'),
    re_path(r'^(?P<pk>\d+)/edit/$', views.edit, name='blog_edit'),
]
