from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from conferences.models import Zosia
from lectures.forms import LectureAdminForm, LectureForm, ScheduleForm
from lectures.models import Lecture, Schedule
from users.models import User
from utils.forms import errors_format, get_durations


@require_http_methods(['GET'])
def index(request):
    """
    Display all accepted lectures
    """
    zosia = Zosia.objects.find_active()
    lectures = Lecture.objects.select_related('author').prefetch_related('supporting_authors') \
        .filter(zosia=zosia).filter(accepted=True)
    ctx = {'objects': lectures}
    return render(request, 'lectures/index.html', ctx)


@staff_member_required()
@require_http_methods(['GET'])
def display_all_staff(request):
    """
    Display all for staff members, they can change acceptation status
    """
    zosia = Zosia.objects.find_active()
    lectures = Lecture.objects.select_related('author').prefetch_related('supporting_authors') \
        .filter(zosia=zosia)
    print([lec.all_authors_names for lec in lectures])
    ctx = {'objects': lectures}
    return render(request, 'lectures/all.html', ctx)


@staff_member_required()
@require_http_methods(['POST'])
def toggle_accept(request):
    """
    ajax for accepting lecture
    """
    lecture_id = request.POST.get('key', None)
    lecture = get_object_or_404(Lecture, pk=lecture_id)
    lecture.toggle_accepted()
    return JsonResponse({'msg': "{} changed status!".format(
        escape(lecture.title))})


@login_required()
def lecture_add(request):
    """
    participant can add his own lecture
    """
    zosia = Zosia.objects.find_active()
    if not zosia.is_lectures_open:
        messages.error(request, _("Call for paper is not open right now!"))
        return redirect(reverse('index'))

    form = LectureForm(request.POST or None)
    ctx = {'form': form}

    if request.method == 'POST':
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.zosia = zosia
            lecture.author = request.user
            lecture.save()
            messages.success(
                request,
                _("Lecture has been saved, it'll be displayed after it's accepted by organizers.")
            )
            return redirect('lectures_index')
        else:
            messages.error(request, errors_format(form))

    return render(request, 'lectures/add.html', ctx)


@staff_member_required()
def lecture_update(request, lecture_id=None):
    """
    Staff member can add lecture for other user, can edit all lectures
    """
    zosia = Zosia.objects.find_active()
    kwargs = {}
    ctx = {}

    if lecture_id:
        lecture = get_object_or_404(Lecture, pk=lecture_id)
        kwargs['instance'] = lecture
        ctx['object'] = lecture

    form = LectureAdminForm(request.POST or None, **kwargs)
    ctx['form'] = form

    if request.method == 'POST':
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.zosia = zosia
            lecture.save()
            form.save_m2m()
            messages.success(request, _("Lecture has been saved."))
            return redirect('lectures_all_staff')
        else:
            messages.error(request, errors_format(form))

    return render(request, 'lectures/add.html', ctx)


def schedule_display(request):
    zosia = Zosia.objects.find_active()
    try:
        schedule = Schedule.objects.get(zosia=zosia)
        ctx = {'schedule': schedule}
        return render(request, 'lectures/schedule.html', ctx)
    except Schedule.DoesNotExist:
        messages.warning(request, _("Schedule is not defined yet."))
        return redirect('lectures_index')


@staff_member_required()
def schedule_update(request):
    zosia = Zosia.objects.find_active()
    schedule, _ = Schedule.objects.get_or_create(zosia=zosia)
    form = ScheduleForm(request.POST or None, instance=schedule)
    ctx = {'form': form, 'zosia': zosia}
    if request.method == 'POST':
        if form.is_valid():
            form.save()
    return render(request, 'lectures/schedule_add.html', ctx)


def load_durations(request):
    lecture_type = request.GET.get("lecture_type")
    author_id = request.GET.get("author")
    author = User.objects.get(pk=author_id) if author_id is not None else request.user
    durations = {'durations': [d[0] for d in get_durations(lecture_type, author)]}
    return JsonResponse(durations)
