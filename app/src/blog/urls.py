from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='blog_index'),
    re_path(r'^create$', views.create, name='blog_create'),
]
