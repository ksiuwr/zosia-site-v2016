from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='lectures_index'),
    url(r'^all$', views.display_all_staff, name='lectures_all_staff'),
    # url(r'^create$', views.update, name='sponsors_add'),
    # url(r'^(?P<sponsor_id>\d+)/$', views.update, name='sponsors_edit'),
    # url(r'^toggle_active/$', views.toggle_active, name='sponsors_toggle_active'),
]
