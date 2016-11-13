from django.conf.urls import url, include

from . import views

urlpatterns = [
    url('^profile/$', views.profile),
    # ^login/$',
    # ^logout/$',
    # ^password_change/$',
    # ^password_change/done/$',
    # ^password_reset/$',
    # ^password_reset/done/$',
    # ^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    # ^reset/done/$',
    url('^', include('django.contrib.auth.urls')),
]
