from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^terms/$', views.terms_and_conditions, name='terms_and_conditions'),
    url(r'^panel/$', views.admin_panel, name='admin'),
    url(r'^user_preferences/$', views.user_preferences_index, name='user_preferences_index'),
    url(r'^user_preferences_toggle_payment_accepted/$',
        views.toggle_payment_accepted, name='user_preferences_toggle_payment_accepted'),
    url(r'^conference/(?P<zosia_id>\d+)/register/$', views.register, name='user_zosia_register'),
    url(r'^user_preferences/(?P<user_preferences_id>\d+)/$', views.user_preferences_edit, name='user_preferences_edit'),
]
