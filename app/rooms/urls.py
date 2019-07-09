from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='rooms_index'),
    path('status/', views.status, name='rooms_status'),
    path('<int:room_id>/join/', views.join, name='rooms_join'),
    path('unlock/', views.unlock, name='rooms_unlock'),
    path('report/', views.report, name='rooms_report'),
    path('import/', views.import_room, name='rooms_import'),
]
