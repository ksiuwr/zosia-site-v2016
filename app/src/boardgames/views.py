from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Boardgame
from .forms import BoardgameForm
from conferences.models import UserPreferences, Zosia
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

@login_required
@require_http_methods(['GET'])
def index(request):
    boardgames = Boardgame.objects.all()
    # boardgames = sorted(boardgames, key=lambda x: x.state)
    try:
        current_zosia = Zosia.objects.find_active()
        preferences = UserPreferences.objects.get(zosia=current_zosia, user=request.user)
    except (Zosia.DoesNotExist, UserPreferences.DoesNotExist):
        ctx = {'boardgames': boardgames}
    else:
        paid = preferences.payment_accepted
        ctx = {'boardgames': boardgames,
            'paid': paid}
    return render(request, 'boardgames/index.html', ctx)


@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    ctx = {'form': BoardgameForm(request.POST or None)}

    if request.method == 'POST':
        if ctx['form'].is_valid():
            ctx['form'].save()
            return redirect('boardgames_index')
    return render(request, 'boardgames/create.html', ctx)


def vote(request):
    ctx = {'boardgames': Boardgame.objects.filter(state="A")}

    if request.method == 'POST':
        pass
    return render(request, 'boardgames/vote.html', ctx)


def accept(request):
    ctx = {'boardgames': Boardgame.objects.filter(state="S")}

    if request.method == 'POST':
        pass
    return render(request, 'boardgames/accept.html', ctx)

