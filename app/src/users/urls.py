from django.contrib.auth.views import LoginView
from django.urls import include, re_path

from users import views
from utils.views import anonymous_required

urlpatterns = [
    re_path(r'^profile/$', views.profile, name='accounts_profile'),
    re_path(r'^signup/$', anonymous_required(views.signup), name='accounts_signup'),
    re_path(r'^edit/$', views.account_edit, name='accounts_edit'),
    re_path(r'^mail/$', views.mail_to_all, name='mail_all'),
    re_path(
        r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='accounts_activate'),
    re_path(r'^login/$',
            anonymous_required(LoginView.as_view(template_name='registration/login.html')),
            name='login'),
    re_path(r'^organizations/$', views.organizations, name='organizations'),
    re_path(r'^organizations/accept/$', views.toggle_organization, name='toggle_organization'),
    re_path(r'^organizations/add/$', views.update_organization, name='organization_add'),
    re_path(r'^organizations/(?P<pk>\d+)/edit/$', views.update_organization,
            name='organization_update'),
    re_path(r'^preferences/$', views.user_preferences_index, name='user_preferences_index'),
    re_path(r'^preferences/admin_edit/$', views.user_preferences_admin_edit,
            name='user_preferences_admin_edit'),
    re_path(r'^preferences/(?P<pk>\d+)/edit$', views.user_preferences_edit,
            name='user_preferences_edit'),
    re_path(r'^preferences/list/all$', views.list_csv_preferences_all,
            name='list_csv_preferences_all'),
    re_path(r'^preferences/list/paid$', views.list_csv_preferences_paid,
            name='list_csv_preferences_paid'),
    re_path(r'^lectures/list/all$', views.list_csv_lectures,
            name='list_csv_lectures'),
    re_path(r'^register/$', views.register, name='user_zosia_register'),
    re_path(r'^', include('django.contrib.auth.urls')),
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
