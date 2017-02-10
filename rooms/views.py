import json

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from conferences.models import Zosia, UserPreferences
from .models import Room, UserRoom
from .serializers import room_to_dict, user_to_dict


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
