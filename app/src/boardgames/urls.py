from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='boardgames_index'),
    # url(r'^create$', views.create, name='blog_create'),
]

# from django.urls import path
# from django.contrib import admin

# from tutorial.views import people

# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path("people/", people)
# ]