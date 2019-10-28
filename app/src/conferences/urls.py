from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^terms/$', views.terms_and_conditions, name='terms_and_conditions'),
    re_path(r'^privacy/$', views.privacy_policy, name='privacy_policy'),
    re_path(r'^panel/$', views.admin_panel, name='admin'),
    re_path(r'^user_preferences/$', views.user_preferences_index, name='user_preferences_index'),
    re_path(r'^user_preferences_admin_edit/$', views.admin_edit,
            name='user_preferences_admin_edit'),
    re_path(r'^conference/(?P<zosia_id>\d+)/register/$', views.register,
            name='user_zosia_register'),
    re_path(r'^user_preferences/(?P<user_preferences_id>\d+)/$', views.user_preferences_edit,
            name='user_preferences_edit'),
    re_path(r'^bus/$', views.bus_admin, name='bus_admin'),
    re_path(r'^bus/add/$', views.bus_add, name='bus_add'),
    re_path(r'^bus/(?P<pk>\d+)/update/$', views.bus_add, name='bus_update'),
    re_path(r'^bus/(?P<pk>\d+)/people/$', views.bus_people, name='bus_people'),
    re_path(r'^conferences/$', views.conferences, name='conferences'),
    re_path(r'^conferences/add/$', views.update_zosia, name='zosia_add'),
    re_path(r'^conferences/(?P<pk>\d+)/update/$', views.update_zosia, name='zosia_update'),
    re_path(r'^conferences/export_data/$', views.export_data, name='export_data'),
    re_path(r'^conferences/export_shirts/$', views.export_shirts, name='export_shirts'),
    re_path(r'^conferences/export_json/$', views.export_json, name='export_json'),
]
