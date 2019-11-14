from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from sponsors.forms import SponsorForm
from sponsors.models import Sponsor


@staff_member_required()
@require_http_methods(['GET'])
def index(request):
    ctx = {'objects': Sponsor.objects.all()}
    return render(request, 'sponsors/index.html', ctx)


@staff_member_required()
@require_http_methods(['POST', 'GET'])
def update(request, sponsor_id=None):
    ctx = {}
    kwargs = {}
    if sponsor_id is not None:
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
@require_http_methods(['POST'])
def toggle_active(request):
    sponsor_id = request.POST.get('key', None)
    sponsor = get_object_or_404(Sponsor, pk=sponsor_id)
    sponsor.toggle_active()
    sponsor.save()
    return JsonResponse({'msg': "{} changed status!".format(
        escape(sponsor.name))})
