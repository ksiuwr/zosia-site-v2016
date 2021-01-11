from django.contrib import admin
from django.db.models import OuterRef, Subquery, Value, Prefetch

from lectures.models import Lecture
from users.models import UserPreferences, User


@admin.register(Lecture)
class UserLectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'author_first_name', 'author_last_name', 'author_email', 'person_type', 'organization')
    readonly_fields = ('organization', 'author_first_name', 'author_last_name', 'author_email', )
    search_fields = ('title', 'author__first_name', 'author__last_name', '_organization')
    list_filter = ('duration', 'person_type')

    def get_queryset(self, request):
        return super().get_queryset(request).only('id', 'title', 'duration', 'person_type', 'author').annotate(
            _organization=Subquery(UserPreferences.objects.filter(user_id=OuterRef('author_id')).values_list(
                'organization__name',
            )[:1]),  # Postgres planner supposedly to join 2 tables, when N+1 complexity is too expensive
        ).prefetch_related(
            Prefetch('author', queryset=User.objects.only('first_name', 'last_name', 'email'))
        )

    def organization(self, obj):
        return obj._organization

    def author_first_name(self, obj):
        return obj.author.first_name
    author_first_name.admin_order_field = 'author__first_name'

    def author_last_name(self, obj):
        return obj.author.last_name
    author_last_name.admin_order_field = 'author__last_name'

    def author_email(self, obj):
        return obj.author.email
