from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, get_object_or_404, redirect, reverse
from sponsors.models import Sponsor
from sponsors.forms import SponsorForm
import json


@staff_member_required()
def index(request):
    ctx = {'objects': Sponsor.objects.all()}
    return render(request, 'sponsors/index.html', ctx)


@staff_member_required()
def update(request, sponsor_id=None):
    ctx = {}
    kwargs = {}
    if sponsor_id:
        sponsor = get_object_or_404(Sponsor, pk=sponsor_id)
        ctx['object'] = sponsor
        kwargs['instance'] = sponsor

    ctx['form'] = SponsorForm(request.POST or None, request.FILES or None,
                              **kwargs)

    if request.method == 'POST':
        if ctx['form'].is_valid():
            ctx['form'].save()
            messages.success(request, _("Form saved!"))
            return redirect(reverse('sponsors_index'))
        else:
            messages.error(request, _("There has been errors"))

    return render(request, 'sponsors/update.html', ctx)


@staff_member_required()
def toggle_active(request):
    if request.method == 'POST':
        sponsor_id = request.POST.get('key', None)
        sponsor = get_object_or_404(Sponsor, pk=sponsor_id)
        sponsor.toggle_active()
        sponsor.save()
        return HttpResponse(json.dumps(
            {'msg': "{} changed status!".format(sponsor.name)}),
            content_type='application/json')
    return HttpResponse(_("It should be post ajax request!"))
