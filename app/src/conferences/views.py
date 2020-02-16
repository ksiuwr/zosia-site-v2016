from collections import Counter
import csv
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from conferences.forms import BusForm, PlaceForm, ZosiaForm
from conferences.models import Bus, Place, Zosia
from lectures.models import Lecture
from rooms.models import Room
from sponsors.models import Sponsor
from users.models import User, UserPreferences
from utils.constants import SHIRT_SIZE_CHOICES, SHIRT_TYPES_CHOICES
from utils.views import csv_response


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
        .values('author__first_name', 'author__last_name', 'title', 'author__organization__name',
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


@staff_member_required
@require_http_methods(['GET'])
def list_by_user(request):
    prefs = UserPreferences.objects.select_related('user').exclude(bus__isnull=True) \
        .order_by("user__last_name", "user__first_name")
    data_list = [(str(p.user), str(p.bus)) for p in prefs]

    return csv_response(("User", "Bus"), data_list, filename='buses_by_users')


@staff_member_required
@require_http_methods(['GET'])
def list_by_bus(request):
    buses = Bus.objects.order_by("departure_time")
    data_list = [(str(b), b.passengers_to_string) for b in buses]

    return csv_response(("Bus", "Users"), data_list, filename='buses_by_bus')


@staff_member_required
@require_http_methods(['GET'])
def statistics(request):
    zosia = Zosia.objects.find_active_or_404()
    user_prefs = UserPreferences.objects.filter(zosia=zosia)

    # data for first chart
    users_count = User.objects.count()
    prefs_count = user_prefs.count()
    paid_count = user_prefs.filter(payment_accepted=True).count()

    users_with_payment = paid_count
    users_with_prefs_only = prefs_count - paid_count
    users_without_prefs = users_count - prefs_count

    # data for second chart
    price_items = Counter([t.price for t in user_prefs]).items()
    price_values, price_counts = zip(*sorted(price_items))

    # other data
    vegetarians = user_prefs.filter(vegetarian=True).count()

    ctx = {
        'registeredUsers': prefs_count,
        'vegetarians': vegetarians,
        'userPrefsData': [users_with_payment, users_with_prefs_only, users_without_prefs],
        'userCostsValues': list(price_values),
        'userCostsCounts': list(price_counts)
    }
    return render(request, 'conferences/statistics.html', ctx)
