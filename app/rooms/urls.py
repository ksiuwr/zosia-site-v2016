from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('', views.index, name='rooms_index'),
    path('status/', views.get_status, name='rooms_status'),
    path('<int:room_id>/join/', views.join, name='rooms_join'),
    path('unlock/', views.unlock, name='rooms_unlock'),
    path('report/', views.report, name='rooms_report'),
    path('import/', views.import_room, name='rooms_import'),
    path('all/', views.RoomListAPI.as_view(), name='all_rooms'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
