import csv
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from conferences.forms import BusForm, PlaceForm, UserPreferencesAdminForm, UserPreferencesForm, ZosiaForm
from conferences.models import Bus, Place, UserPreferences, Zosia
from lectures.models import Lecture
from rooms.models import Room
from sponsors.models import Sponsor
from utils.constants import ADMIN_USER_PREFERENCES_COMMAND_CHANGE_BONUS, \
    ADMIN_USER_PREFERENCES_COMMAND_TOGGLE_PAYMENT, MAX_BONUS_MINUTES, MIN_BONUS_MINUTES, \
    PAYMENT_GROUPS, SHIRT_SIZE_CHOICES, SHIRT_TYPES_CHOICES
from utils.forms import errors_format


@staff_member_required()
@require_http_methods(['GET'])
def export_json(request):
    zosia = get_object_or_404(Zosia, active=True)
    prefs = UserPreferences.objects \
        .filter(zosia=zosia) \
        .values('user__first_name', 'user__last_name', 'user__email',
                'organization_id__name', 'bus_id', 'accommodation_day_1',
                'dinner_day_1', 'accommodation_day_2', 'breakfast_day_2', 'dinner_day_2',
                'accommodation_day_3', 'breakfast_day_3', 'dinner_day_3', 'breakfast_day_4',
                'contact', 'information', 'vegetarian', 'payment_accepted',
                'shirt_size', 'shirt_type')

    rooms = Room.objects \
        .values('members__first_name', 'members__last_name', 'name')

    lectures = Lecture.objects \
        .filter(zosia=zosia) \
        .values('author__first_name', 'author__last_name', 'title',
                'abstract', 'description')

    data = {
        "lectures": list(lectures),
        "preferences": list(prefs),
        "rooms": list(rooms),
    }

    return JsonResponse(data)


@staff_member_required()
@require_http_methods(['GET'])
def export_shirts(request):
    zosia = get_object_or_404(Zosia, active=True)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="shirts.csv"'

    writer = csv.writer(response)
    writer.writerow(['Size', 'Type', 'Registered', 'Payed'])
    for shirt_size in SHIRT_SIZE_CHOICES:
        for shirt_type in SHIRT_TYPES_CHOICES:
            reg_count = UserPreferences.objects \
                .filter(zosia=zosia, shirt_size=shirt_size[0], shirt_type=shirt_type[0]) \
                .count()
            pay_count = UserPreferences.objects. \
                filter(zosia=zosia, shirt_size=shirt_size[0], shirt_type=shirt_type[0],
                       payment_accepted=True) \
                .count()
            writer.writerow([shirt_size[1], shirt_type[1], reg_count, pay_count])

    return response


@staff_member_required()
@require_http_methods(['GET'])
def export_data(request):
    ctx = {}
    return render(request, 'conferences/export_data.html', ctx)


@staff_member_required()
@require_http_methods(['GET'])
def user_preferences_index(request):
    zosia = get_object_or_404(Zosia, active=True)
    # TODO: paging?
    user_preferences = UserPreferences.objects.filter(
        zosia=zosia).select_related('user').order_by('pk').all()
    ctx = {'objects': user_preferences,
           'change_bonus': ADMIN_USER_PREFERENCES_COMMAND_CHANGE_BONUS,
           'toggle_payment': ADMIN_USER_PREFERENCES_COMMAND_TOGGLE_PAYMENT,
           'min_bonus': MIN_BONUS_MINUTES,
           'max_bonus': MAX_BONUS_MINUTES}
    return render(request, 'conferences/user_preferences_index.html', ctx)


@staff_member_required()
@require_http_methods(['GET', 'POST'])
def user_preferences_edit(request, user_preferences_id=None):
    ctx = {}
    kwargs = {}
    if user_preferences_id is not None:
        user_preferences = get_object_or_404(UserPreferences, pk=user_preferences_id)
        ctx['object'] = user_preferences
        kwargs['instance'] = user_preferences

    form = UserPreferencesAdminForm(request.POST or None, **kwargs)
    ctx['form'] = form

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, _("Form saved!"))
            return redirect(reverse('user_preferences_index'))
        else:
            messages.error(request, errors_format(form))

    return render(request, 'conferences/user_preferences_edit.html', ctx)


@staff_member_required()
@require_http_methods(['POST'])
def admin_edit(request):
    user_preferences_id = request.POST.get('key', None)
    user_preferences = get_object_or_404(UserPreferences, pk=user_preferences_id)
    command = request.POST.get('command', False)
    if command == ADMIN_USER_PREFERENCES_COMMAND_TOGGLE_PAYMENT:
        status = user_preferences.toggle_payment_accepted()
        user_preferences.save()
        return JsonResponse({'msg': _("Changed payment status of {} to {}").format(
            escape(user_preferences.user.get_full_name()),
            status),
            'status': status})
    if command == ADMIN_USER_PREFERENCES_COMMAND_CHANGE_BONUS:
        user_preferences.bonus_minutes = request.POST.get('bonus', user_preferences.bonus_minutes)
        user_preferences.save()
        return JsonResponse({'msg': _("Changed bonus of {} to {}").format(
            escape(user_preferences.user.get_full_name()),
            user_preferences.bonus_minutes),
            'bonus': user_preferences.bonus_minutes})

    return Http404()


@require_http_methods(['GET'])
def index(request):
    zosia = Zosia.objects.find_active()
    sponsors = Sponsor.objects.filter(is_active=True)
    context = {
        'zosia': zosia,
        'sponsors': sponsors
    }
    if zosia is not None:
        query = {
            'key': settings.GAPI_KEY,
            'q': zosia.place.address,
        }
        context['gapi_place_src'] = settings.GAPI_PLACE_BASE_URL + '?' + urlencode(query)
        # FIXME: Make sure this url starts with http. Django WILL try to make it relative otherwise
        context['zosia_url'] = zosia.place.url
    return render(request, 'conferences/index.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def register(request, zosia_id):
    zosia = get_object_or_404(Zosia, pk=zosia_id)
    ctx = {'field_dependencies': PAYMENT_GROUPS, 'payed': False, 'zosia': zosia}
    form_args = {}

    user_prefs = UserPreferences.objects.filter(zosia=zosia, user=request.user).first()

    if user_prefs is not None:
        ctx['object'] = user_prefs
        form_args['instance'] = user_prefs

    form = UserPreferencesForm(request.user, request.POST or None, **form_args)
    ctx['form'] = form

    if user_prefs and user_prefs.payment_accepted:
        ctx['payed'] = True
        form.disable()

    if request.method == 'POST':
        if form.is_valid():
            form.call(zosia)
            messages.success(request, _("Form saved!"))
            return redirect('accounts_profile')
        else:
            messages.error(request, errors_format(form))

    return render(request, 'conferences/register.html', ctx)


@require_http_methods(['GET'])
def terms_and_conditions(request):
    zosia = Zosia.objects.find_active()
    if zosia is None:
        raise Http404
    ctx = {'zosia': zosia}
    return render(request, 'conferences/terms_and_conditions.html', ctx)


@require_http_methods(['GET'])
def privacy_policy(request):
    return render(request, 'conferences/privacy_policy.html')


@staff_member_required
@require_http_methods(['GET'])
def admin_panel(request):
    return render(request, 'conferences/admin.html')


@staff_member_required
@require_http_methods(['GET'])
def bus_admin(request):
    zosia = Zosia.objects.find_active()
    active_buses = Bus.objects.filter(zosia=zosia)
    ctx = {'zosia': zosia, 'buses': active_buses}
    return render(request, 'conferences/bus.html', ctx)


@staff_member_required
@require_http_methods(['GET'])
def bus_people(request, pk):
    bus = get_object_or_404(Bus, pk=pk)
    users = UserPreferences.objects.select_related('user').filter(bus=bus)
    ctx = {'bus': bus, 'users': users}
    return render(request, 'conferences/bus_users.html', ctx)


@staff_member_required
@require_http_methods(['GET', 'POST'])
def bus_add(request, pk=None):
    active_zosia = Zosia.objects.find_active()
    if pk is not None:
        instance = get_object_or_404(Bus, pk=pk)
        form = BusForm(request.POST or None, initial={'zosia': active_zosia},
                       instance=instance)
    else:
        instance = None
        form = BusForm(request.POST or None, initial={'zosia': active_zosia})

    if form.is_valid():
        form.save()
        messages.success(request, _('Bus has been saved'))
        return redirect('bus_admin')
    ctx = {'form': form, 'object': instance}
    return render(request, 'conferences/bus_add.html', ctx)


@staff_member_required
@require_http_methods(['GET'])
def conferences(request):
    conferences = Zosia.objects.all()
    ctx = {'conferences': conferences}
    return render(request, 'conferences/conferences.html', ctx)


@staff_member_required
@require_http_methods(['GET', 'POST'])
def update_zosia(request, pk=None):
    if pk is not None:
        zosia = get_object_or_404(Zosia, pk=pk)
        form = ZosiaForm(request.POST or None, instance=zosia)
    else:
        zosia = None
        form = ZosiaForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, _('Zosia has been saved'))
        return redirect('conferences')

    ctx = {'form': form, 'zosia': zosia}
    return render(request, 'conferences/conference_add.html', ctx)


@staff_member_required
@require_http_methods(['GET'])
def place(request):
    places = Place.objects.filter()
    ctx = {'places': places}
    return render(request, 'conferences/place.html', ctx)


@staff_member_required
@require_http_methods(['GET', 'POST'])
def place_add(request, pk=None):
    if pk is not None:
        instance = get_object_or_404(Place, pk=pk)
        form = PlaceForm(request.POST or None, instance=instance)
    else:
        instance = None
        form = PlaceForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, _('Place has been saved'))
        return redirect('place')
    ctx = {'form': form, 'object': instance}
    return render(request, 'conferences/place_add.html', ctx)
