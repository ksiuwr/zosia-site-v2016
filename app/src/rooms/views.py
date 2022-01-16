import csv
from io import TextIOWrapper
import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.views.decorators.vary import vary_on_cookie

from conferences.models import Zosia
from rooms.forms import UploadFileForm
from rooms.models import Room
from rooms.serializers import room_to_dict
from users.models import UserPreferences
from utils.views import csv_response, validation_format


@cache_page(60 * 15)  # Cache hard (15mins)
@vary_on_cookie
@login_required
@require_http_methods(['GET'])
def index(request):
    # Return HTML w/ rooms layout
    try:
        zosia = Zosia.objects.get(active=True)
    except Zosia.DoesNotExist:
        messages.error(request, _('There is no active conference'))
        return redirect(reverse('index'))

    try:
        preferences = UserPreferences.objects.get(zosia=zosia, user=request.user)
    except UserPreferences.DoesNotExist:
        messages.error(request, _('Please register first'))
        return redirect(reverse('user_zosia_register'))

    if preferences.room is not None and preferences.room.hidden:
        messages.error(request, _('Your are already assigned to hidden room by organizators'))
        return redirect(reverse('accounts_profile'))

    paid = preferences.payment_accepted
    if not paid:
        messages.error(request, _('Your payment must be accepted first'))
        return redirect(reverse('accounts_profile'))

    if not zosia.is_rooming_open:
        messages.error(request, _('Room registration is not active yet'))
        return redirect(reverse('accounts_profile'))

    if zosia.is_rooming_over:
        messages.error(request, _('Room registration is over'))
        return redirect(reverse('accounts_profile'))

    rooms = Room.objects.all_visible().prefetch_related('members').all()
    rooms = sorted(rooms, key=lambda x: x.pk)
    rooms_json = json.dumps(list(map(room_to_dict, rooms)))
    context = {
        'rooms': rooms,
        'rooms_json': rooms_json,
    }
    return render(request, 'rooms/index.html', context)


@staff_member_required
@require_http_methods(['GET'])
def list_csv_room_by_user(request):
    prefs = UserPreferences.objects.prefetch_related("user").order_by("user__last_name",
                                                                      "user__first_name")
    data_list = [(str(p.user), str(p.room) if p.room else '', str(p.payment_accepted))
                 for p in prefs]
    return csv_response(("User", "Room", "Paid"), data_list, filename='list_csv_room_by_user')


@staff_member_required
@require_http_methods(['GET'])
def list_csv_room_by_member(request):
    prefs = UserPreferences.objects.prefetch_related("user") \
        .filter(user__room_of_user__isnull=False).order_by("user__last_name", "user__first_name")
    data_list = [(str(p.user), str(p.room)) for p in prefs]
    return csv_response(("User", "Room"), data_list, filename='list_csv_room_by_member')


@staff_member_required
@require_http_methods(['GET'])
def list_csv_members_by_room(request):
    rooms = Room.objects.prefetch_related('members').all()
    data_list = [(str(r), r.members_to_string) for r in sorted(rooms, key=Room.name_to_key_orderable)]
    return csv_response(("Room", "Members"), data_list, filename='list_csv_members_by_room')


def handle_uploaded_file(csvfile):
    rooms = []

    for line, row in enumerate(csv.reader(csvfile, delimiter=','), start=1):
        try:
            name, desc, hidden, av_single, av_double, b_single, b_double = row
        except ValueError as e:
            raise ValidationError("Line %(line)s - %(error)s", code="invalid",
                                  params={"line": line, "error": e})

        if name != "Name":
            rooms.append(
                Room(name=name, description=desc, hidden=hidden,
                     available_beds_single=av_single,
                     available_beds_double=av_double, beds_single=b_single,
                     beds_double=b_double))

    try:
        Room.objects.bulk_create(rooms)
    except ValueError:
        raise ValidationError(
            "Could not add rooms, check whether the file is properly formed and all values are correct.",
            code="invalid")


@staff_member_required
@require_http_methods(['GET', 'POST'])
def import_room(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                handle_uploaded_file(TextIOWrapper(request.FILES['file'].file,
                                                   encoding=request.encoding))
            except ValidationError as e:
                messages.error(request,
                               validation_format(e, _("There were errors when adding rooms")))
            except Exception:
                messages.error(request, _("There were errors when adding rooms"))
            else:
                messages.success(request, _("Rooms have been successfully added"))
                return HttpResponseRedirect(reverse('admin'))
    else:
        form = UploadFileForm()

    return render(request, 'rooms/import.html', {'form': form})
