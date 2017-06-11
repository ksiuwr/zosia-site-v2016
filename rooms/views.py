import json
import csv
from io import TextIOWrapper

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.template import loader, Context

from conferences.models import Zosia, UserPreferences
from .models import Room, UserRoom
from .serializers import room_to_dict, user_to_dict
from .forms import UploadFileForm


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

    rooming_open = zosia.is_rooming_open
    if not rooming_open:
        messages.error(request, _('Room registration is not active yet'))
        return redirect(reverse('accounts_profile'))

    rooms = Room.objects.for_zosia(zosia).prefetch_related('users').all()
    rooms = sorted(rooms, key=lambda x: x.pk)
    rooms_json = json.dumps(list(map(room_to_dict, rooms)))
    context = {
        'rooms': rooms,
        'rooms_json': rooms_json,
    }
    return render(request, 'rooms/index.html', context)


# GET
@vary_on_cookie
@login_required
@require_http_methods(['GET'])
def status(request):
    # Ajax
    # Return JSON view of rooms
    zosia = get_object_or_404(Zosia, active=True)
    can_start_rooming = zosia.can_start_rooming(get_object_or_404(UserPreferences, zosia=zosia, user=request.user))
    rooms = Room.objects.for_zosia(zosia).select_related('lock').prefetch_related('users').all()
    rooms_view = []
    for room in rooms:
        dic = room_to_dict(room)
        dic['owns'] = room.is_locked and room.lock.owns(request.user) and room.lock.password
        dic['people'] = list(map(user_to_dict, room.users.all()))
        dic['inside'] = request.user.pk in map(lambda x: x.pk, room.users.all())
        rooms_view.append(dic)

    view = {
        'can_start_rooming': can_start_rooming,
        'rooms': rooms_view,
    }
    return JsonResponse(view)


@login_required
@require_http_methods(['POST'])
def join(request, room_id):
    zosia = get_object_or_404(Zosia, active=True)
    room = get_object_or_404(Room, zosia=zosia, pk=room_id)
    password = request.POST.get('password', '')
    if not zosia.can_start_rooming(get_object_or_404(UserPreferences, zosia=zosia, user=request.user)):
        return JsonResponse({'error': 'cannot_room_yet'}, status=400)

    should_lock = request.POST.get('lock', True) in [True, 'True', '1', 'on', 'true']
    result = room.join(request.user, password=password, lock=should_lock)
    if type(result) is ValidationError:
        return JsonResponse({'status': result.message}, status=400)
    else:
        return JsonResponse({'status': 'ok'})


@login_required
@require_http_methods(['POST'])
def unlock(request):
    zosia = get_object_or_404(Zosia, active=True)
    room = get_object_or_404(UserRoom, room__zosia=zosia, user=request.user).room
    if not zosia.is_rooming_open:
        return JsonResponse({'status': 'time_passed'}, status=400)
    result = room.unlock(request.user)
    if result:
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'not_changed'})


# https://docs.djangoproject.com/en/1.11/howto/outputting-csv/
# NOTE: Might not be the best approach - consider using csv module instead
def csv_response(data, template, filename='file'):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
    t = loader.get_template(template)
    c = Context({
        'data': data,
    })
    response.write(t.render(c))
    return response


@staff_member_required
@require_http_methods(['GET'])
def report(request):
    zosia = get_object_or_404(Zosia, active=True)
    rooms = Room.objects.for_zosia(zosia).prefetch_related('users').all()
    rooms = sorted(rooms, key=lambda x: str(x))
    users = UserPreferences.objects.for_zosia(zosia).prefetch_related('user').all()
    users = sorted(users, key=lambda x: str(x))
    ctx = {
        'zosia':  zosia,
        'rooms': rooms,
        'user_preferences': users
    }

    download = request.GET.get('download', False)
    if download == 'users':
        return csv_response(users, template='rooms/users.txt', filename='users')
    if download == 'rooms':
        return csv_response(rooms, template='rooms/rooms.txt', filename='rooms')

    return render(request, 'rooms/report.html', ctx)


def handle_uploaded_file(zosia, csvfile):
    for row in csv.reader(csvfile, delimiter=','):
        name, desc, cap, hidden = row
        if name != "Name":
            Room.objects.get_or_create(
                zosia=zosia,
                name=name,
                description=desc,
                capacity=cap,
                hidden=hidden)


@staff_member_required
@require_http_methods(['GET', 'POST'])
def import_room(request):
    zosia = get_object_or_404(Zosia, active=True)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(zosia, TextIOWrapper(request.FILES['file'].file, encoding=request.encoding))
            return HttpResponseRedirect(reverse('rooms_report'))
    else:
        form = UploadFileForm()
    return render(request, 'rooms/import.html', {'form': form})
