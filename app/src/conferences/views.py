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

from conferences.forms import PlaceForm, TransportForm, ZosiaForm
from conferences.models import Place, Transport, Zosia
from lectures.models import Lecture
from organizers.models import OrganizerContact
from sponsors.models import Sponsor
from users.models import User, UserPreferences
from utils.constants import SHIRT_SIZE_CHOICES, SHIRT_TYPES_CHOICES
from utils.views import csv_response


@staff_member_required()
@require_http_methods(['GET'])
def export_data(request):
    zosia = Zosia.objects.find_active_or_404()

    prefs = UserPreferences.objects \
        .filter(zosia=zosia) \
        .values('user__first_name', 'user__last_name', 'user__email', 'user__person_type',
                'organization__name', 'transport__name', 'transport__departure_time',
                'accommodation_day_1', 'dinner_day_1', 'accommodation_day_2', 'breakfast_day_2',
                'dinner_day_2', 'accommodation_day_3', 'breakfast_day_3', 'dinner_day_3',
                'breakfast_day_4', 'contact', 'information', 'vegetarian', 'payment_accepted',
                'shirt_size', 'shirt_type', 'is_student', 'transport_baggage')

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
def transport(request):
    zosia = Zosia.objects.find_active()
    transports = Transport.objects.filter(zosia=zosia)
    ctx = {'zosia': zosia, 'transports': transports}
    return render(request, 'conferences/transport.html', ctx)


@staff_member_required
@require_http_methods(['GET'])
def transport_people(request, pk):
    transport_obj = get_object_or_404(Transport, pk=pk)
    users = UserPreferences.objects.select_related('user').filter(transport=transport_obj)
    ctx = {'transport': transport_obj, 'users': users}
    return render(request, 'conferences/transport_people.html', ctx)


@staff_member_required
@require_http_methods(['GET', 'POST'])
def transport_add(request, pk=None):
    active_zosia = Zosia.objects.find_active()
    if pk is not None:
        instance = get_object_or_404(Transport, pk=pk)
        form = TransportForm(request.POST or None, initial={'zosia': active_zosia},
                             instance=instance)
    else:
        instance = None
        form = TransportForm(request.POST or None, initial={'zosia': active_zosia})

    if form.is_valid():
        form.save()
        messages.success(request, _('Transport has been saved'))
        return redirect('transport')
    ctx = {'form': form, 'object': instance}
    return render(request, 'conferences/transport_add.html', ctx)


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
def list_csv_transport_by_user(request):
    prefs = UserPreferences.objects.select_related('user').filter(transport__isnull=False) \
        .order_by("user__last_name", "user__first_name")
    data_list = [(str(p.user), str(p.transport), str(p.payment_accepted)) for p in prefs]
    return csv_response(("User", "Transport", "Paid"), data_list,
                        filename='list_csv_transport_by_user')


@staff_member_required
@require_http_methods(['GET'])
def list_csv_all_users_by_transport(request):
    transport_list = Transport.objects.order_by("departure_time")
    data_list = [(str(t), t.passengers_to_string()) for t in transport_list]
    return csv_response(("Transport", "All users"), data_list,
                        filename='list_csv_all_users_by_transport')


@staff_member_required
@require_http_methods(['GET'])
def list_csv_paid_users_by_transport(request):
    transport_list = Transport.objects.order_by("departure_time")
    data_list = [(str(t), t.passengers_to_string(paid=True)) for t in transport_list]
    return csv_response(("Transport", "Paid users"), data_list,
                        filename='list_csv_paid_users_by_transport')


@staff_member_required
@require_http_methods(['GET'])
def list_csv_paid_students_by_transport(request):
    transport_list = Transport.objects.order_by("departure_time")
    data_list = [(str(t), t.passengers_to_string(paid=True, is_student=True))
                 for t in transport_list]
    return csv_response(("Transport", "Paid student users"), data_list,
                        filename='list_csv_paid_student_users_by_transport')


@staff_member_required
@require_http_methods(['GET'])
def list_csv_paid_non_students_by_transport(request):
    transport_list = Transport.objects.order_by("departure_time")
    data_list = [(str(t), t.passengers_to_string(paid=True, is_student=False))
                 for t in transport_list]
    return csv_response(("Transport", "Paid non-student users"), data_list,
                        filename='list_csv_paid_non_student_users_by_transport')


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

    # data for transport info chart
    transport_list = Transport.objects.all()
    transport_labels = []
    transport_values = {'paid': [], 'notPaid': [], 'empty': []}
    for t in transport_list:
        transport_labels.append(f'{t}')
        transport_values['paid'].append(t.paid_passengers_count)
        transport_values['notPaid'].append(t.passengers_count - t.paid_passengers_count)
        transport_values['empty'].append(t.free_seats)

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
        'transportLabels': json.dumps(transport_labels),
        'transportValues': json.dumps(transport_values),
        'numberOfTransport': len(transport_labels)
    }
    return render(request, 'conferences/statistics.html', ctx)
