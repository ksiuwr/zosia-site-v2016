from collections import Counter
import csv
import json
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from conferences.forms import BusForm, PlaceForm, ZosiaForm
from conferences.models import Bus, Place, Zosia
from lectures.models import Lecture
from organizers.models import OrganizerContact
from sponsors.models import Sponsor
from users.models import User, UserPreferences
from utils.constants import SHIRT_SIZE_CHOICES, SHIRT_TYPES_CHOICES
from utils.views import csv_response


@staff_member_required()
@require_http_methods(['GET'])
def export_json(request):
    zosia = Zosia.objects.find_active_or_404()

    prefs = UserPreferences.objects \
        .filter(zosia=zosia) \
        .values('user__first_name', 'user__last_name', 'user__email', 'user__person_type',
                'organization__name', 'bus__name', 'bus__departure_time', 'accommodation_day_1',
                'dinner_day_1', 'accommodation_day_2', 'breakfast_day_2', 'dinner_day_2',
                'accommodation_day_3', 'breakfast_day_3', 'dinner_day_3', 'breakfast_day_4',
                'contact', 'information', 'vegetarian', 'payment_accepted',
                'shirt_size', 'shirt_type')

    lectures = Lecture.objects \
        .filter(zosia=zosia) \
        .values('author__first_name', 'author__last_name', 'title', 'abstract',
                'author__preferences__organization__name', 'description')

    sponsors = Sponsor.objects \
        .values('name', 'sponsor_type', 'path_to_logo')

    organizers_contacts = OrganizerContact.objects \
        .filter(zosia=zosia) \
        .values('user__first_name', 'user__last_name', 'phone_number')

    data = {
        "zosia": {
            "start_date": zosia.start_date,
            "end_date": zosia.end_date
        },
        "contacts": list(organizers_contacts),
        "lectures": list(lectures),
        "preferences": list(prefs),
        "sponsors": list(sponsors)
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


@require_http_methods(['GET'])
def index(request):
    user = request.user
    zosia = Zosia.objects.find_active()
    sponsors = Sponsor.objects.filter(is_active=True)

    context = {
        'zosia': zosia,
        'sponsors': sponsors,
    }

    if zosia is not None:
        query = {
            'key': settings.GAPI_KEY,
            'q': zosia.place.address,
        }
        context.update({
            'gapi_place_src': settings.GAPI_PLACE_BASE_URL + '?' + urlencode(query),
            # FIXME: Make sure this url starts with http.
            #  Django WILL try to make it relative otherwise
            'zosia_url': zosia.place.url,
            'registration_open': zosia.is_user_registration_open(user)
        })

    return render(request, 'conferences/index.html', context)


@require_http_methods(['GET'])
def terms_and_conditions(request):
    zosia = Zosia.objects.find_active()
    ctx = {'zosia': zosia}
    return render(request, 'conferences/terms_and_conditions.html', ctx)


@require_http_methods(['GET'])
def privacy_policy(request):
    return render(request, 'conferences/privacy_policy.html')


@require_http_methods(['GET'])
def sign_up_rules_for_invited(request):
    return render(request, 'conferences/sign_up_rules_for_invited.html')


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
    all_conferences = Zosia.objects.all()
    ctx = {'conferences': all_conferences}
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
def list_csv_bus_by_user(request):
    prefs = UserPreferences.objects.select_related('user').filter(bus__isnull=False) \
        .order_by("user__last_name", "user__first_name")
    data_list = [(str(p.user), str(p.bus), str(p.payment_accepted)) for p in prefs]
    return csv_response(("User", "Bus", "Paid"), data_list, filename='list_csv_bus_by_user')


@staff_member_required
@require_http_methods(['GET'])
def list_csv_all_users_by_bus(request):
    buses = Bus.objects.order_by("departure_time")
    data_list = [(str(b), b.passengers_to_string()) for b in buses]
    return csv_response(("Bus", "All users"), data_list, filename='list_csv_all_users_by_bus')


@staff_member_required
@require_http_methods(['GET'])
def list_csv_paid_users_by_bus(request):
    buses = Bus.objects.order_by("departure_time")
    data_list = [(str(b), b.passengers_to_string(paid=True)) for b in buses]
    return csv_response(("Bus", "Paid users"), data_list, filename='list_csv_paid_users_by_bus')


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
    if len(user_prefs):
        price_items = Counter([t.price for t in user_prefs]).items()
        price_values, price_counts = zip(*sorted(price_items))
    else:
        price_values, price_counts = [], []

    # data for bus info chart
    buses = Bus.objects.all()
    buses_labels = []
    buses_values = {'paid': [], 'notPaid': [], 'empty': []}
    for bus in buses:
        buses_labels.append(f'{bus}')
        buses_values['paid'].append(bus.paid_passengers_count)
        buses_values['notPaid'].append(bus.passengers_count - bus.paid_passengers_count)
        buses_values['empty'].append(bus.free_seats)

    # discount
    discounts = list(
        user_prefs.filter(discount_round__gt=0).values_list('discount_round', flat=True))

    # discount_values = {
    #     "round_1": (discounts.count(1), zosia.first_discount_limit),
    #     "round_2": (discounts.count(2), zosia.second_discount_limit),
    #     "round_3": (discounts.count(3), zosia.third_discount_limit)
    #     }

    discount_values = {
        "taken": [discounts.count(x) for x in (1, 2, 3)],
        "available": [
            zosia.first_discount_limit-discounts.count(1),
            zosia.second_discount_limit-discounts.count(2),
            zosia.third_discount_limit-discounts.count(3)]
    }

    # other data
    vegetarians = user_prefs.filter(vegetarian=True).count()
    students = user_prefs.filter(is_student=True).count()

    ctx = {
        'registeredUsers': prefs_count,
        'vegetarians': vegetarians,
        'students': students,
        'discountsData': json.dumps(discount_values),
        'userPrefsData': [users_with_payment, users_with_prefs_only, users_without_prefs],
        'userCostsValues': list(price_values),
        'userCostsCounts': list(price_counts),
        'busesLabels': json.dumps(buses_labels),
        'busesValues': json.dumps(buses_values),
        'numberOfBuses': len(buses_labels)
    }
    return render(request, 'conferences/statistics.html', ctx)
