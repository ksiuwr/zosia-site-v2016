from urllib.parse import urlencode

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required

from .models import Zosia


GAPI_PLACE_BASE_URL = "https://www.google.com/maps/embed/v1/place"


def index(request):
    zosia = Zosia.objects.find_active()
    context = {
        'zosia': zosia,
    }
    if zosia:
        query = {
            'key': settings.GAPI_KEY,
            'q': zosia.place.address,
        }
        context['gapi_place_src'] = GAPI_PLACE_BASE_URL + '?' + urlencode(query)
    return render(request, 'conferences/index.html', context)

@login_required
def register(request, zosia_id):
    zosia = get_object_or_404(Zosia, pk=zosia_id)
    context = {
        'zosia': zosia,
    }
    return render(request, 'conferences/register.html', context)
