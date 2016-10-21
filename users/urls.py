from django.conf.urls import url, include

from . import views

urlpatterns = [
    url('^profile/$', views.profile),
    url('^', include('django.contrib.auth.urls')),
]
