from django.contrib import admin

from conferences.models import Bus, Place, UserPreferences, Zosia

for model in [Zosia, Bus, Place, UserPreferences]:
    admin.site.register(model)
