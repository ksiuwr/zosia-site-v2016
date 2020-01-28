from django.contrib import admin

from rooms.models import Room, UserRoom

admin.site.register(Room)
admin.site.register(UserRoom)
