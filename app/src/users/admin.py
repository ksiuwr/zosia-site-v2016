from django.contrib import admin
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Exists, OuterRef, Q, Value
from django.db.models.functions import Concat

from lectures.models import Lecture
from rooms.models import Room, UserRoom
from users.models import Organization, User, UserPreferences, UserFilters
from utils.constants import SHIRT_SIZE_CHOICES, SHIRT_TYPES_CHOICES

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


class HavePreferencesListFilter(admin.SimpleListFilter):
    title = 'have preferences'
    parameter_name = 'have_preferences'

    def lookups(self, request, model_admin):
        return (
            ('true', 'Have any preference'),
            ('false', "Don't have any preference"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'true':
            return queryset.filter(_have_preferences=True)
        if value == 'false':
            return queryset.filter(_have_preferences=False)
        return queryset


class PaymentAcceptedListFilter(admin.SimpleListFilter):
    title = 'payment accepted'
    parameter_name = 'payment_accepted'

    def lookups(self, request, model_admin):
        return (
            ('true', 'Have payment accepted'),
            ('false', "Don't have payment accepted"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'true':
            return queryset.filter(_payment_accepted__contains=[True])
        if value == 'false':
            return queryset.filter(Q(_payment_accepted__contains=[False]) | Q(_payment_accepted=[None]))
        return queryset


class HaveLectureListFilter(admin.SimpleListFilter):
    title = 'have lecture'
    parameter_name = 'have_lecture'

    def lookups(self, request, model_admin):
        return (
            ('true', 'Have lecture'),
            ('false', "Don't have lecture"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'true':
            return queryset.filter(_have_lectures=True)
        if value == 'false':
            return queryset.filter(_have_lectures=False)
        return queryset


class RoomNameListFilter(admin.SimpleListFilter):
    title = 'room name'
    parameter_name = 'room_name'

    def lookups(self, request, model_admin):
        return (('No room', 'No room'),) + tuple((r.name, r.name) for r in sorted(Room.objects.only('name').distinct(), key=Room.name_to_key_orderable))

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'No room':
            return queryset.filter(_room_name=[None])
        elif value:
            return queryset.filter(_room_name__contains=[value])


class ShirtPropertiesListFilter(admin.SimpleListFilter):
    title = 'shirt properties'
    parameter_name = 'shirt_properties'

    def lookups(self, request, model_admin):
        return [(f'{size}-{type_}', f'{size}-{type_}') for type_, _t in SHIRT_TYPES_CHOICES
                for size, _s in SHIRT_SIZE_CHOICES]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            shirt_size, shirt_type = value.split('-')
            return queryset.filter(preferences__shirt_size=shirt_size, preferences__shirt_type=shirt_type)


class RoomInline(admin.TabularInline):
    model = UserRoom


class UserPreferencesInline(admin.TabularInline):
    model = UserPreferences
    fk_name = 'user'
    extra = 1


@admin.register(UserFilters)
class UserFiltersAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'room_name', 'payment_accepted', 'have_preferences', 'have_lecture',
                    'shirt_properties')
    list_display_links = ('first_name', 'last_name')
    fields = ('first_name', 'last_name', 'room_name', 'payment_accepted', 'have_preferences', 'have_lecture',
              'shirt_properties')
    readonly_fields = ('room_name', 'payment_accepted', 'have_preferences', 'have_lecture', 'shirt_properties')
    search_fields = ('first_name', 'last_name', '_room_name')
    list_filter = (PaymentAcceptedListFilter, HaveLectureListFilter, HavePreferencesListFilter,
                   ShirtPropertiesListFilter, RoomNameListFilter)
    inlines = (UserPreferencesInline, RoomInline)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _have_preferences=Exists(UserPreferences.objects.filter(user=OuterRef('id')).only('user')),
            _room_name=ArrayAgg('room_of_user__name', distinct=True),
            _payment_accepted=ArrayAgg('preferences__payment_accepted'),
            _shirt_properties=ArrayAgg(Concat('preferences__shirt_size', Value('-'), 'preferences__shirt_type')),
            _have_lectures=Exists(Lecture.objects.filter(author=OuterRef('id')).only('author')),
        )

    def shirt_properties(self, obj):
        return obj._shirt_properties
    shirt_properties.admin_order_field = '_shirt_properties'

    def room_name(self, obj):
        return obj._room_name

    room_name.admin_order_field = '_room_name'

    def payment_accepted(self, obj):  # FK from Many site, User can have many UserPreferences. Maybe link with related id should be provided.
        return obj._payment_accepted

    def have_preferences(self, obj):
        return obj._have_preferences

    have_preferences.boolean = True

    def have_lecture(self, obj):
        return obj._have_lectures

    have_lecture.boolean = True


admin.site.register(Organization, OrganizationAdmin)
