from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='questions_index'),
    re_path(r'^all/$', views.index_for_staff, name='questions_index_staff'),
    re_path(r'^add/$', views.update, name='questions_add'),
    re_path(r'^(?P<question_id>\d+)/$', views.update, name='questions_edit'),
    re_path(r'^(?P<question_id>\d+)/delete/$', views.delete, name='questions_delete'),
]
