from django.contrib import admin
from django.db.models import OuterRef, Prefetch, Subquery

from lectures.models import Lecture
from users.models import User, UserPreferences


@admin.register(Lecture)
class UserLectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'lecture_type', 'accepted', 'author_first_name',
                    'author_last_name', 'author_email', 'author_person_type', 'organization')
    readonly_fields = ('author_first_name', 'author_last_name', 'author_email',
                       'author_person_type', 'organization')
    search_fields = ('title', 'author__first_name', 'author__last_name', 'author_organization')
    list_filter = ('lecture_type', 'accepted', 'duration', 'author__person_type')

    def get_queryset(self, request):
        return super().get_queryset(request).only('id', 'title', 'duration', 'author').annotate(
            author_organization=Subquery(
                UserPreferences.objects.filter(user_id=OuterRef('author_id')).values_list(
                    'organization__name'
                )[:1]
            ),
            # Postgres planner supposedly to join 2 tables, when N+1 complexity is too expensive
        ).prefetch_related(
            Prefetch('author',
                     queryset=User.objects.only('first_name', 'last_name', 'email', 'person_type'))
        )

    def organization(self, obj):
        return obj.author_organization

    # @admin.display(ordering='author__first_name')
    def author_first_name(self, obj):
        return obj.author.first_name

    author_first_name.admin_order_field = 'author__first_name'

    # @admin.display(ordering='author__last_name')
    def author_last_name(self, obj):
        return obj.author.last_name

    author_last_name.admin_order_field = 'author__last_name'

    def author_email(self, obj):
        return obj.author.email

    def author_person_type(self, obj):
        return obj.author.person_type
