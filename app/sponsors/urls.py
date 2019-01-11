from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='sponsors_index'),
    url(r'^create$', views.update, name='sponsors_add'),
    url(r'^(?P<sponsor_id>\d+)/$', views.update, name='sponsors_edit'),
    url(r'^toggle_active/$', views.toggle_active, name='sponsors_toggle_active'),
]
