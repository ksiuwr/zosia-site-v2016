from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.decorators.http import require_http_methods
from django.utils.translation import ugettext_lazy as _
from conferences.models import Zosia
from .forms import LectureForm, LectureAdminForm, ScheduleForm
from .models import Lecture, Schedule


@require_http_methods(['GET'])
def index(request):
    """
    Display all accepted lectures
    """
    zosia = Zosia.objects.find_active()
    lectures = Lecture.objects.select_related('author').filter(
                zosia=zosia).filter(accepted=True)
    ctx = {'objects': lectures}
    return render(request, 'lectures/index.html', ctx)


@staff_member_required()
@require_http_methods(['GET'])
def display_all_staff(request):
    """
    Display all for staff members, they can change acceptation status
    """
    zosia = Zosia.objects.find_active()
    lectures = Lecture.objects.select_related('author').filter(zosia=zosia)
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
    return JsonResponse({'msg': "{} changed status!".format(lecture.title)})


@login_required()
def lecture_add(request):
    """
    participant can add his own lecture
    """
    zosia = Zosia.objects.find_active()
    if not zosia.lectures_open():
        messages.error(request, _("Call for paper is not open right now!"))
        return redirect(reverse('index'))

    ctx = {'form': LectureForm(request.POST or None)}
    if request.method == 'POST':
        if ctx['form'].is_valid():
            lecture = ctx['form'].save(commit=False)
            lecture.zosia = zosia
            lecture.author = request.user
            lecture.save()
            messages.success(request, _("Lecture has been saved"))
            return redirect('lectures_index')
        else:
            messages.error(request, _("Please review your form"))
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
    ctx['form'] = LectureAdminForm(request.POST or None, **kwargs)
    if request.method == 'POST':
        if ctx['form'].is_valid():
            lecture = ctx['form'].save(commit=False)
            lecture.zosia = zosia
            lecture.save()
            messages.success(request, _("Lecture has been saved"))
            return redirect('lectures_all_staff')
        else:
            messages.error(request, _('Please review your form'))
    return render(request, 'lectures/add.html', ctx)


def schedule_display(request):
    zosia = Zosia.objects.find_active()
    schedule = get_object_or_404(Schedule, zosia=zosia)
    ctx = {'schedule': schedule}
    return render(request, 'lectures/schedule.html', ctx)


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
