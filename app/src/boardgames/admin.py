from django.contrib import admin
from .models import Boardgame
from .models import Vote

for model in [Boardgame, Vote]:
    admin.site.register(model)
