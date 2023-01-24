from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from organizers.forms import OrganizerForm
from organizers.models import OrganizerContact

from utils.forms import errors_format

@staff_member_required()
@require_http_methods(['GET'])
def index(request):
    ctx = {'objects': OrganizerContact.objects.all()}
    return render(request, 'organizers/index.html', ctx)

@staff_member_required()
@require_http_methods(['POST', 'GET'])
def update(request, user_id=None):
    ctx = {}
    kwargs = {}
    organizer = None
    
    if user_id is not None:
        organizer = get_object_or_404(OrganizerContact, pk=user_id)
        ctx['object'] = organizer
        kwargs['instance'] = organizer

    form = OrganizerForm(request.POST or None, **kwargs)

    ctx['form'] = form
    ctx['organizer'] = organizer

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, _("Form saved!"))
            return redirect(reverse('organizers_index'))
        else:
            messages.error(request, errors_format(form))

    return render(request, 'organizers/update.html', ctx)

@staff_member_required()
@require_http_methods(['GET'])
def delete(request, user_id):
    organiser = get_object_or_404(OrganizerContact, pk=user_id)
    organiser.delete()
    return redirect('organizers_index')