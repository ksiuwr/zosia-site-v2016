from django.contrib import admin

from users.models import Organization, User, UserPreferences

admin.site.register(User)
admin.site.register(UserPreferences)


def accept_organization(modeladmin, request, queryset):
    for organ in queryset:
        organ.accepted = True
        organ.save()


def reject_organization(modeladmin, request, queryset):
    for organ in queryset:
        organ.accepted = False
        organ.save()


accept_organization.short_description = 'Accept selected organizations'
reject_organization.short_description = 'Reject selected organizations'


class OrganizationAdmin(admin.ModelAdmin):
    actions = [accept_organization, reject_organization, ]


admin.site.register(Organization, OrganizationAdmin)
