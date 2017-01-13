from urllib.parse import urlencode

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from .models import Zosia, UserPreferences
from .forms import UserPreferencesForm
from sponsors.models import Sponsor


GAPI_PLACE_BASE_URL = "https://www.google.com/maps/embed/v1/place"


@require_http_methods(['GET'])
def index(request):
    zosia = Zosia.objects.find_active()
    sponsors = Sponsor.objects.filter(is_active=True)
    context = {
        'zosia': zosia,
        'sponsors': sponsors
    }
    if zosia:
        query = {
            'key': settings.GAPI_KEY,
            'q': zosia.place.address,
        }
        context['gapi_place_src'] = GAPI_PLACE_BASE_URL + '?' + urlencode(query)
        # FIXME: Make sure this url is absolute. Django WILL try to make it relative if it doesn't start with http
        context['zosia_url'] = zosia.place.url
    return render(request, 'conferences/index.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def register(request, zosia_id):
    zosia = get_object_or_404(Zosia, pk=zosia_id)
    field_dependencies = UserPreferencesForm.DEPENDENCIES
    ctx = {
        'field_dependencies': field_dependencies
    }
    form_args = {}

    user_prefs = UserPreferences.objects.filter(zosia=zosia, user=request.user).first()
    if user_prefs:
        ctx['object'] = user_prefs
        form_args['instance'] = user_prefs

    form = UserPreferencesForm(request.POST or None,
                               **form_args)

    if user_prefs and user_prefs.payment_accepted:
        form.disable()

    ctx['form'] = form
    if request.method == 'POST':
        if form.is_valid():
            form.call(zosia, request.user)
            messages.success(request, _("Form saved!"))
            return redirect('accounts_profile')
        else:
            messages.error(request, _("There were errors"))

    return render(request, 'conferences/register.html', ctx)


@require_http_methods(['GET'])
def terms_and_conditions(request):
    return render(request, 'conferences/terms_and_conditions.html')
