from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='blog_index'),
    url(r'^create$', views.create, name='blog_create'),
]
