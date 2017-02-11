from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<zosia_id>\d+)/register$', views.register, name='user_zosia_register'),
    url(r'^terms/$', views.terms_and_conditions, name='terms_and_conditions'),
    url(r'^panel/$', views.admin_panel, name='admin'),
]
