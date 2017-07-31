from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^terms/$', views.terms_and_conditions, name='terms_and_conditions'),
    url(r'^panel/$', views.admin_panel, name='admin'),
    url(r'^user_preferences/$', views.user_preferences_index, name='user_preferences_index'),
    url(r'^user_preferences_admin_edit/$',
        views.admin_edit, name='user_preferences_admin_edit'),
    url(r'^conference/(?P<zosia_id>\d+)/register/$', views.register, name='user_zosia_register'),
    url(r'^user_preferences/(?P<user_preferences_id>\d+)/$', views.user_preferences_edit, name='user_preferences_edit'),
    url(r'^bus/$', views.bus_admin, name='bus_admin'),
    url(r'^bus/add/$', views.bus_add, name='bus_add'),
    url(r'^bus/(?P<pk>\d+)/update/$', views.bus_add, name='bus_update'),
    url(r'^bus/(?P<pk>\d+)/people/$', views.bus_people, name='bus_people'),
]
