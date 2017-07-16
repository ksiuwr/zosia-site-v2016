from django.contrib import admin
from .models import Zosia, Bus, Place, UserPreferences

for model in [Zosia, Bus, Place, UserPreferences]:
    admin.site.register(model)
