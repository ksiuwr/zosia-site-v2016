from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.utils.translation import ugettext_lazy as _
from conferences.models import Zosia
from .forms import LectureForm, LectureAdminForm
from .models import Lecture


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
    # TODO: create
    pass


@login_required()
def lecture_add(request):
    """
    participant can add his own lecture
    """
    # TODO: review view
    zosia = Zosia.objects.find_active()
    ctx = {'form': LectureForm(request.POST or None)}
    if request.method == 'POST':
        if ctx['form'].is_valid():
            lecture = ctx['form'].save(commit=False)
            lecture.zosia = zosia
            lecture.author = request.user
            messages.succes(request, _("Lecture has been saved"))
            return redirect('lectures_index')
        else:
            messages.error(request, _("Please review your form"))
    return render(request, 'lectures/add.html', ctx)


@staff_member_required()
def lecture_update(request):
    """
    Staff member can add lecture for other user, can edit all lectures
    """
    # TODO: create
    pass


def schedule_display(request):
    # TODO: create
    pass
