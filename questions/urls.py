from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='questions_index'),
    url(r'^all/$', views.index_for_staff, name='questions_index_staff'),
]
