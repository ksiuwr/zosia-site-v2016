from django.urls import path

from rooms import views

urlpatterns = [
    path('', views.index, name='rooms_index'),
    path('list/byuser', views.list_by_user, name='rooms_list_by_user'),
    path('list/byroom', views.list_by_room, name='rooms_list_by_room'),
    path('import/', views.import_room, name='rooms_import'),
]
