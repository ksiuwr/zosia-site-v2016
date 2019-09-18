from django.contrib import admin
from .models import Boardgame

for model in [Boardgame]:
    admin.site.register(model)
