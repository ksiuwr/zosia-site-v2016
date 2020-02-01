from django.contrib import admin
from boardgames.models import Boardgame
from boardgames.models import Vote

for model in [Boardgame, Vote]:
    admin.site.register(model)
