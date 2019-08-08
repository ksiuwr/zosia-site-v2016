from django.contrib import admin
from .models import Organization, User

admin.site.register(User)


def accept_organization(modeladmin, request, queryset):
    for organ in queryset:
        organ.accepted = True
        organ.save()


accept_organization.short_description = 'Accept selected organizations'


def reject_organization(modeladmin, request, queryset):
    for organ in queryset:
        organ.accepted = False
        organ.save()


reject_organization.short_description = 'Reject selected organizations'


class OrganizationAdmin(admin.ModelAdmin):
    actions = [accept_organization, reject_organization, ]


admin.site.register(Organization, OrganizationAdmin)
