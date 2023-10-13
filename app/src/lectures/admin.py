from django.contrib import admin
from django.db.models import BooleanField, Case, Exists, OuterRef, Prefetch, Subquery, Value, When

from lectures.models import Lecture
from users.models import User, UserPreferences


class HasSupportersNamesListFilter(admin.SimpleListFilter):
    title = 'has supporters names'
    parameter_name = 'has_supporters_names'

    def lookups(self, request, model_admin):
        return [
            ('true', "Supporters names provided"),
            ('false', "No supporters provided"),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'true':
            return queryset.filter(has_supporters_names=True)
        if value == 'false':
            return queryset.filter(has_supporters_names=False)
        return queryset


class HasSupportingAuthorsListFilter(admin.SimpleListFilter):
    title = 'has supporting authors'
    parameter_name = 'has_supporting_authors'

    def lookups(self, request, model_admin):
        return [
            ('true', "Has supporting authors"),
            ('false', "No supporting authors"),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'true':
            return queryset.filter(has_supporting_authors=True)
        if value == 'false':
            return queryset.filter(has_supporting_authors=False)
        return queryset


@admin.register(Lecture)
class UserLectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'lecture_type', 'accepted', 'author_first_name',
                    'author_last_name', 'author_email', 'author_person_type', 'author_organization',
                    'has_supporting_authors', 'has_supporters_names')
    readonly_fields = ('author_first_name', 'author_last_name', 'author_email',
                       'author_person_type', 'author_organization', 'supporters_names',
                       'has_supporters_names', 'has_supporting_authors')
    search_fields = ('title', 'author__first_name', 'author__last_name', 'author_organization')
    list_filter = ('lecture_type', 'accepted', 'duration', 'author__person_type',
                   HasSupportingAuthorsListFilter, HasSupportersNamesListFilter)

    def get_queryset(self, request):
        return super().get_queryset(request).only('id', 'title', 'duration', 'author').annotate(
            author_organization=Subquery(
                UserPreferences.objects.filter(user_id=OuterRef('author_id')).values_list(
                    'organization__name'
                )[:1]
            ),
            has_supporters_names=Case(
                When(supporters_names__isnull=True, then=Value(False)),
                When(supporters_names__exact="", then=Value(False)),
                default=Value(True),
                output_field=BooleanField()
            ),
            has_supporting_authors=Exists(
                User.objects.filter(lectures_supporting__pk=OuterRef('pk')).only('id')
            )
        ).prefetch_related(
            Prefetch('author',
                     queryset=User.objects.only('first_name', 'last_name', 'email', 'person_type'))
        )

    @admin.display(boolean=True)
    def has_supporting_authors(self, obj):
        return obj.has_supporting_authors

    @admin.display(boolean=True)
    def has_supporters_names(self, obj):
        return obj.has_supporters_names

    def author_organization(self, obj):
        return obj.author_organization

    @admin.display(ordering='author__first_name')
    def author_first_name(self, obj):
        return obj.author.first_name

    @admin.display(ordering='author__last_name')
    def author_last_name(self, obj):
        return obj.author.last_name

    def author_email(self, obj):
        return obj.author.email

    def author_person_type(self, obj):
        return obj.author.person_type
