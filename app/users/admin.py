from django.contrib import admin
from .models import Organization, User

for model in [User, Organization]:
    admin.site.register(model)
