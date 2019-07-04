from django.conf.urls import url, include
from django.contrib.auth.views import LoginView

from . import views
from .utils import anonymous_required


urlpatterns = [
    url(r'^profile/$', views.profile, name='accounts_profile'),
    url(r'^signup/$', anonymous_required(views.signup), name='accounts_signup'),
    url(r'^edit/$', views.account_edit, name='accounts_edit'),
    url(r'^mail/$', views.mail_to_all, name='mail_all'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='accounts_activate'),
    url(r'^login/$', anonymous_required(LoginView.as_view(template_name='registration/login.html')), name='login'),
    url(r'^ajax/organization/create', views.create_organization, name='create_organization'),
    url(r'^organizations/$', views.organizations, name='organizations'),
    url(r'^organizations/accept/$', views.toggle_organization, name='toggle_organization'),
    url(r'^organizations/add/$', views.update_organization, name='organization_add'),
    url(r'^organizations/(?P<pk>\d+)/edit/$', views.update_organization, name='organization_update'),
    url(r'^', include('django.contrib.auth.urls')),
    # NOTE: it adds following URLs:
    # ^logout/$ [name='logout']
    # ^password_change/$ [name='password_change']
    # ^password_change/done/$ [name='password_change_done']
    # ^password_reset/$ [name='password_reset']
    # ^password_reset/done/$ [name='password_reset_done']
    # ^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$
    #   [name='password_reset_confirm']
    # ^reset/done/$ [name='password_reset_complete']
]
