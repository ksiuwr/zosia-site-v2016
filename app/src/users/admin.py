from django.contrib import admin
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Exists, OuterRef, Q, Value
from django.db.models.functions import Concat

from lectures.models import Lecture
from rooms.models import Room, UserRoom
from users.models import Organization, User, UserFilters, UserPreferences
from utils.constants import SHIRT_SIZE_CHOICES, SHIRT_TYPES_CHOICES


def accept_organization(modeladmin, request, queryset):
    for org in queryset:
        org.accepted = True
        org.save()


def reject_organization(modeladmin, request, queryset):
    for org in queryset:
        org.accepted = False
        org.save()


accept_organization.short_description = 'Accept selected organizations'
reject_organization.short_description = 'Reject selected organizations'


class OrganizationAdmin(admin.ModelAdmin):
    actions = [accept_organization, reject_organization]


class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'hash', 'person_type', 'is_active',
                    'is_staff', 'is_superuser', 'last_login')
    list_display_links = ('first_name', 'last_name')
    readonly_fields = ('email', 'hash', 'last_login', 'password')
    search_fields = ('first_name', 'last_name', 'email', 'hash')
    list_filter = ('person_type', 'is_active', 'is_staff', 'is_superuser')


class HavePreferencesListFilter(admin.SimpleListFilter):
    title = 'has preferences'
    parameter_name = 'has_preferences'

    def lookups(self, request, model_admin):
        return (
            ('true', 'Have any preference'),
            ('false', "Don't have any preference"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'true':
            return queryset.filter(has_preferences=True)
        if value == 'false':
            return queryset.filter(has_preferences=False)
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
            return queryset.filter(payment_accepted__contains=[True])
        if value == 'false':
            return queryset.filter(
                Q(payment_accepted__contains=[False]) | Q(payment_accepted=[None]))
        return queryset


class HaveLectureListFilter(admin.SimpleListFilter):
    title = 'has lecture'
    parameter_name = 'has_lecture'

    def lookups(self, request, model_admin):
        return (
            ('true', 'Have lecture'),
            ('false', "Don't have lecture"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'true':
            return queryset.filter(has_lectures=True)
        if value == 'false':
            return queryset.filter(has_lectures=False)
        return queryset


class RoomNameListFilter(admin.SimpleListFilter):
    title = 'room name'
    parameter_name = 'room_name'

    def lookups(self, request, model_admin):
        return (('No room', 'No room'),) + tuple((r.name, r.name) for r in
                                                 sorted(Room.objects.only('name').distinct(),
                                                        key=Room.name_to_key_orderable))

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'No room':
            return queryset.filter(room_name=[None])
        elif value:
            return queryset.filter(room_name__contains=[value])


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
            return queryset.filter(preferences__shirt_size=shirt_size,
                                   preferences__shirt_type=shirt_type)


class RoomInline(admin.TabularInline):
    model = UserRoom


class UserPreferencesInline(admin.TabularInline):
    model = UserPreferences
    fk_name = 'user'
    extra = 1


@admin.register(UserFilters)
class UserFiltersAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'room_name', 'payment_accepted', 'has_preferences',
                    'has_lecture', 'shirt_properties')
    list_display_links = ('first_name', 'last_name')
    fields = ('first_name', 'last_name', 'room_name', 'payment_accepted', 'has_preferences',
              'has_lecture', 'shirt_properties')
    readonly_fields = ('room_name', 'payment_accepted', 'has_preferences', 'has_lecture',
                       'shirt_properties')
    search_fields = ('first_name', 'last_name', 'room_name')
    list_filter = (PaymentAcceptedListFilter, HaveLectureListFilter,
                   HavePreferencesListFilter, ShirtPropertiesListFilter, RoomNameListFilter)
    inlines = (UserPreferencesInline, RoomInline)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            has_preferences=Exists(
                UserPreferences.objects.filter(user=OuterRef('id')).only('user')),
            room_name=ArrayAgg('room_of_user__name', distinct=True),
            payment_accepted=ArrayAgg('preferences__payment_accepted'),
            shirt_properties=ArrayAgg(
                Concat('preferences__shirt_size', Value('-'), 'preferences__shirt_type')),
            has_lectures=Exists(Lecture.objects.filter(author=OuterRef('id')).only('author')),
        )

    def shirt_properties(self, obj):
        return obj.shirt_properties

    shirt_properties.admin_order_field = 'shirt_properties'

    def room_name(self, obj):
        return obj.room_name

    room_name.admin_order_field = 'room_name'

    def payment_accepted(self, obj):
        # FK from Many site, User can have many UserPreferences.
        # Maybe link with related id should be provided.
        return obj.payment_accepted

    def has_preferences(self, obj):
        return obj.has_preferences

    has_preferences.boolean = True

    def has_lecture(self, obj):
        return obj.has_lectures

    has_lecture.boolean = True


admin.site.register(User, UserAdmin)
admin.site.register(UserPreferences)
admin.site.register(Organization, OrganizationAdmin)
