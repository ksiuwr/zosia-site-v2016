from django.urls import path

from lectures import views

urlpatterns = [
    path('', views.index, name='lectures_index'),
    path('all', views.display_all_staff, name='lectures_all_staff'),
    path('add', views.lecture_add, name='lectures_add'),
    path('create', views.lecture_update, name='lectures_staff_add'),
    path('<int:lecture_id>/', views.lecture_update, name='lectures_edit'),
    path('accept/', views.toggle_accept, name="lectures_toggle_accept"),
    path('schedule/', views.schedule_display, name='lectures_schedule'),
    path('schedule/update/', views.schedule_update, name='lectures_schedule_add'),
    path('durations/', views.load_durations, name='load_durations')
]
