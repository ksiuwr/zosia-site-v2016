from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='lectures_index'),
    re_path(r'^all$', views.display_all_staff, name='lectures_all_staff'),
    re_path(r'^add$', views.lecture_add, name='lectures_add'),
    re_path(r'^create$', views.lecture_update, name='lectures_staff_add'),
    re_path(r'^(?P<lecture_id>\d+)/$', views.lecture_update, name='lectures_edit'),
    re_path(r'^toggleaccepted/$', views.toggle_accept, name="lectures_toggle_accept"),
    re_path(r'^schedule/$', views.schedule_display, name='lectures_schedule'),
    re_path(r'^schedule/update/$', views.schedule_update, name='lectures_schedule_add'),
]
