from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render, reverse
from .models import Boardgame, Vote
from .forms import BoardgameForm
from conferences.models import UserPreferences, Zosia
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from django.http import Http404, HttpResponse, JsonResponse
import json

@login_required
@require_http_methods(['GET'])
def index(request):
    boardgames = Boardgame.objects.all()
    boardgames = sorted(boardgames, key=lambda x: x.accepted, reverse=True)
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


@login_required
@require_http_methods(['GET','POST'])
def vote(request):
    votes = Vote.objects.filter(user=request.user).values_list('boardgame', flat=True)
    print(list(votes))
    ctx = {'boardgames': Boardgame.objects.filter(accepted=True),
    'user_voted': list(votes) }
    if request.method == 'POST':
        old_ids = json.loads(request.POST.get('old_ids'))
        new_ids = json.loads(request.POST.get('new_ids'))
        common_ids = [x for x in old_ids if x in new_ids]
        old_ids = [x for x in old_ids if not x in common_ids]
        new_ids = [x for x in new_ids if not x in common_ids]
        for x in old_ids:
            boardgame = get_object_or_404(Boardgame, pk=x)
            boardgame.votes_down()
            boardgame.save() 
            Vote.objects.get(boardgame=x).delete()
        for x in new_ids:
            boardgame = get_object_or_404(Boardgame, pk=x)
            boardgame.votes_up()
            boardgame.save()
            vote = Vote(user=request.user, boardgame=boardgame)
            vote.save()
        return JsonResponse({'old_ids': old_ids, 'new_ids': new_ids})
    return render(request, 'boardgames/vote.html', ctx)


@staff_member_required
@require_http_methods(['GET','POST'])
def accept(request):
    boardgames = Boardgame.objects.all()
    boardgames = sorted(boardgames, key=lambda x: x.accepted, reverse=True)    
    accepted = Boardgame.objects.filter(accepted=True).values_list('id', flat=True)
    print(list(accepted))
    ctx = {'boardgames': boardgames, 'accepted': list(accepted)}

    if request.method == 'POST':
        old_ids = json.loads(request.POST.get('old_ids'))
        new_ids = json.loads(request.POST.get('new_ids'))
        common_ids = [x for x in old_ids if x in new_ids]
        old_ids = [x for x in old_ids if not x in common_ids]
        new_ids = [x for x in new_ids if not x in common_ids]
        for x in old_ids:
            boardgame = get_object_or_404(Boardgame, pk=x)
            boardgame.toggle_accepted()
            boardgame.save()
        for x in new_ids:
            boardgame = get_object_or_404(Boardgame, pk=x)
            boardgame.toggle_accepted()
            boardgame.save()
        return JsonResponse({'old_ids': old_ids, 'new_ids': new_ids})
    return render(request, 'boardgames/accept.html', ctx)

