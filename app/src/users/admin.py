from django.contrib import admin
from django.db.models import Exists, F, OuterRef, Q, Value
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
    readonly_fields = ('email', 'hash', 'last_login')
    search_fields = ('first_name', 'last_name', 'email', 'hash')
    list_filter = ('person_type', 'is_active', 'is_staff', 'is_superuser')


class OrganizationNameListFilter(admin.SimpleListFilter):
    title = 'organization name'
    parameter_name = 'organization_name'

    def lookups(self, request, model_admin):
        return [('none', 'No organization')] + \
            [(org.name, org.name) for org in
             sorted(Organization.objects.only('name').distinct(), key=lambda org: org.name)]

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'none':
            return queryset.filter(organization_name__isnull=True)
        if value:
            return queryset.filter(organization_name=value)
        return queryset


class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_accepted', 'organization_name', 'accommodation_day_1',
                    'accommodation_day_2', 'accommodation_day_3', 'vegetarian', 'bonus_minutes')
    readonly_fields = ('user', 'zosia', 'terms_accepted')
    list_filter = ('payment_accepted', OrganizationNameListFilter, 'accommodation_day_1',
                   'accommodation_day_2', 'accommodation_day_3', 'vegetarian')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            organization_name=F('organization__name')
        )

    @admin.display(ordering='organization_name')
    def organization_name(self, obj):
        return obj.organization_name


class HasPreferencesListFilter(admin.SimpleListFilter):
    title = 'has preferences'
    parameter_name = 'has_preferences'

    def lookups(self, request, model_admin):
        return [
            ('true', 'Has any preference'),
            ('false', "Doesn't have any preference"),
        ]

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
        return [
            ('true', 'Payment accepted'),
            ('false', "Payment not accepted"),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'true':
            return queryset.filter(payment_accepted=True)
        if value == 'false':
            return queryset.filter(Q(payment_accepted=False) | Q(payment_accepted__isnull=True))
        return queryset


class HasLectureListFilter(admin.SimpleListFilter):
    title = 'has lecture'
    parameter_name = 'has_lecture'

    def lookups(self, request, model_admin):
        return [
            ('author', 'As author'),
            ('supporter', 'As supporting author'),
            ('none', "Doesn't have lecture"),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'author':
            return queryset.filter(has_lecture=True)
        if value == 'supporter':
            return queryset.filter(has_supporting_lecture=True)
        if value == 'none':
            return queryset.filter(has_lecture=False, has_supporting_lecture=False)
        return queryset


class RoomNameListFilter(admin.SimpleListFilter):
    title = 'room name'
    parameter_name = 'room_name'

    def lookups(self, request, model_admin):
        return [('none', 'No room')] + \
            [(r.name, r.name) for r in
             sorted(Room.objects.only('name').distinct(), key=Room.name_to_key_orderable)]

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'none':
            return queryset.filter(room_name__isnull=True)
        if value:
            return queryset.filter(room_name=value)
        return queryset


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
        return queryset


class RoomInline(admin.TabularInline):
    model = UserRoom


class UserPreferencesInline(admin.TabularInline):
    model = UserPreferences
    fk_name = 'user'
    extra = 1


@admin.register(UserFilters)
class UserFiltersAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'room_name', 'payment_accepted', 'has_preferences',
                    'has_lecture', 'has_supporting_lecture', 'shirt_properties')
    list_display_links = ('first_name', 'last_name')
    fields = ('first_name', 'last_name', 'room_name', 'payment_accepted', 'has_preferences',
              'has_lecture', 'has_supporting_lecture', 'shirt_properties')
    readonly_fields = ('room_name', 'payment_accepted', 'has_preferences', 'has_lecture',
                       'has_supporting_lecture', 'shirt_properties')
    search_fields = ('first_name', 'last_name', 'room_name')
    list_filter = (PaymentAcceptedListFilter, HasPreferencesListFilter, HasLectureListFilter,
                   RoomNameListFilter, ShirtPropertiesListFilter)
    inlines = (UserPreferencesInline, RoomInline)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            has_preferences=Exists(
                UserPreferences.objects.filter(user=OuterRef('id')).only('user')
            ),
            room_name=F('room_of_user__name'),
            payment_accepted=F('preferences__payment_accepted'),
            shirt_properties=Concat('preferences__shirt_size', Value('-'),
                                    'preferences__shirt_type')
            ,
            has_lecture=Exists(
                Lecture.objects.filter(author=OuterRef('id')).only('id')
            ),
            has_supporting_lecture=Exists(
                Lecture.objects.filter(supporting_authors__id=OuterRef('id')).only('id')
            )
        )

    @admin.display(ordering='shirt_properties')
    def shirt_properties(self, obj):
        return obj.shirt_properties

    @admin.display(ordering='room_name')
    def room_name(self, obj):
        return obj.room_name

    def payment_accepted(self, obj):
        # FK from Many site, User can have many UserPreferences.
        # Maybe link with related id should be provided.
        return obj.payment_accepted

    @admin.display(boolean=True)
    def has_preferences(self, obj):
        return obj.has_preferences

    @admin.display(boolean=True)
    def has_lecture(self, obj):
        return obj.has_lecture

    @admin.display(boolean=True)
    def has_supporting_lecture(self, obj):
        return obj.has_supporting_lecture


admin.site.register(User, UserAdmin)
admin.site.register(UserPreferences, UserPreferencesAdmin)
admin.site.register(Organization, OrganizationAdmin)
