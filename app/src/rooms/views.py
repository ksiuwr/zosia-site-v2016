import csv
from io import TextIOWrapper
import json
import re

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.views.decorators.vary import vary_on_cookie

from conferences.models import UserPreferences, Zosia
from rooms.forms import UploadFileForm
from rooms.models import Room
from rooms.serializers import room_to_dict


# Cache hard (15mins)
@cache_page(60 * 15)
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
        return redirect(reverse('user_zosia_register', kwargs={'zosia_id': zosia.pk}))

    paid = preferences.payment_accepted
    if not paid:
        messages.error(request, _('Your payment must be accepted first'))
        return redirect(reverse('accounts_profile'))

    if not zosia.is_rooming_open:
        messages.error(request, _('Room registration is not active yet'))
        return redirect(reverse('accounts_profile'))

    rooms = Room.objects.all_visible().prefetch_related('members').all()
    rooms = sorted(rooms, key=lambda x: x.pk)
    rooms_json = json.dumps(list(map(room_to_dict, rooms)))
    context = {
        'rooms': rooms,
        'rooms_json': rooms_json,
    }
    return render(request, 'rooms/index.html', context)


def csv_response(header, data, filename='file'):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    writer = csv.writer(response)
    writer.writerow(header)

    for row in data:
        writer.writerow(row)

    return response


@staff_member_required
@require_http_methods(['GET'])
def list_by_user(request):
    def to_key(user_name):
        user_name = user_name.lower()
        m = re.match(r"(\w+) (\w+)", user_name)

        return tuple(reversed(m.groups()))

    prefs = UserPreferences.objects.all()
    data_list = sorted(([p.user.display_name, str(p.room) if p.room else ''] for p in prefs),
                       key=lambda e: to_key(e[0]))

    return csv_response(("User", "Room"), data_list, filename='rooms_by_users')


@staff_member_required
@require_http_methods(['GET'])
def list_by_room(request):
    def to_key(room_name):
        room_name = room_name.lower()
        m = re.match(r"(\D?)(\d*)(.*)", room_name[::-1])
        g = [x[::-1] for x in reversed(m.groups())]

        return (g[0], int(g[1]), g[2]) if g[1] != '' else (room_name, 0, '')

    rooms = Room.objects.prefetch_related('members').all()
    data_list = sorted(([str(r), r.members_to_string] for r in rooms),
                       key=lambda e: to_key(e[0]))

    return csv_response(("Room", "Users"), data_list, filename='rooms_by_room')


def handle_uploaded_file(csvfile):
    rooms = []
    for row in csv.reader(csvfile, delimiter=','):
        name, desc, cap, hidden = row
        if name != "Name":
            rooms.append(
                Room(name=name, description=desc, capacity=cap, hidden=hidden))
    Room.objects.bulk_create(rooms)


@staff_member_required
@require_http_methods(['GET', 'POST'])
def import_room(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(TextIOWrapper(request.FILES['file'].file,
                                               encoding=request.encoding))
            return HttpResponseRedirect(reverse('rooms_report'))
    else:
        form = UploadFileForm()
    return render(request, 'rooms/import.html', {'form': form})
