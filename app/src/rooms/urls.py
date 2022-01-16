from django.urls import path

from rooms import views

urlpatterns = [
    path('', views.index, name='rooms_index'),
    path('list/roombyuser', views.list_csv_room_by_user, name='list_csv_room_by_user'),
    path('list/roombymember', views.list_csv_room_by_member, name='list_csv_room_by_member'),
    path('list/membersbyroom', views.list_csv_members_by_room,
         name='list_csv_members_by_room'),
    path('import/', views.import_room, name='rooms_import'),
]
