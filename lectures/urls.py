from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='lectures_index'),
    url(r'^all$', views.display_all_staff, name='lectures_all_staff'),
    url(r'^add$', views.lecture_add, name='lectures_add'),
    url(r'^create$', views.lecture_update, name='lectures_staff_add'),
    url(r'^(?P<lecture_id>\d+)/$', views.lecture_update, name='lectures_edit'),
    url(r'^toggleaccepted/$', views.toggle_accept, name="lectures_toggle_accept"),
]
