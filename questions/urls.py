from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='questions_index'),
    url(r'^all/$', views.index_for_staff, name='questions_index_staff'),
    url(r'^add/$', views.update, name='questions_add'),
    url(r'^(?P<question_id>\d+)/$', views.update, name='questions_edit'),
    url(r'^(?P<question_id>\d+)/delete/$', views.delete, name='questions_delete'),
]
