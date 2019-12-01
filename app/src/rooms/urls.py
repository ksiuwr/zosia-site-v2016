from django.urls import path

from rooms import views

urlpatterns = [
    path('', views.index, name='rooms_index'),
    path('status/', views.status, name='rooms_status'),
    path('report/', views.report, name='rooms_report'),
    path('import/', views.import_room, name='rooms_import'),
]
