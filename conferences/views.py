from urllib.parse import urlencode

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.decorators.http import require_http_methods
from django.http import Http404, JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.translation import ugettext_lazy as _

from .models import Zosia, UserPreferences
from .forms import UserPreferencesForm, UserPreferencesAdminForm
from sponsors.models import Sponsor


GAPI_PLACE_BASE_URL = "https://www.google.com/maps/embed/v1/place"


@staff_member_required()
@require_http_methods(['GET'])
def user_preferences_index(request):
    zosia = get_object_or_404(Zosia, active=True)
    ctx = {'objects': UserPreferences.objects.filter(zosia=zosia).all()}
    return render(request, 'conferences/user_preferences_index.html', ctx)


@staff_member_required()
@require_http_methods(['GET', 'POST'])
def user_preferences_edit(request, user_preferences_id=None):
    ctx = {}
    kwargs = {}
    if user_preferences_id:
        user_preferences = get_object_or_404(UserPreferences, pk=user_preferences_id)
        ctx['object'] = user_preferences
        kwargs['instance'] = user_preferences

    ctx['form'] = UserPreferencesAdminForm(request.POST or None,
                                           **kwargs)

    if request.method == 'POST':
        if ctx['form'].is_valid():
            ctx['form'].save()
            messages.success(request, _("Form saved!"))
            return redirect(reverse('user_preferences_index'))
        else:
            messages.error(request, _("There has been errors"))

    return render(request, 'conferences/user_preferences_edit.html', ctx)


@staff_member_required()
@require_http_methods(['POST'])
def toggle_payment_accepted(request):
    user_preferences_id = request.POST.get('key', None)
    user_preferences = get_object_or_404(UserPreferences, pk=user_preferences_id)
    user_preferences.toggle_payment_accepted()
    user_preferences.save()
    return JsonResponse({'msg': "{} changed status!".format(user_preferences.user.get_full_name())})


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
    zosia = Zosia.objects.find_active()
    if not zosia:
        raise Http404
    ctx = {'zosia': zosia}
    return render(request, 'conferences/terms_and_conditions.html', ctx)


@staff_member_required
@require_http_methods(['GET'])
def admin_panel(request):
    return render(request, 'conferences/admin.html')
