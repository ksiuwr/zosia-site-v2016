import json
import re

from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Count
from urllib.request import urlopen

from boardgames.models import Boardgame, Vote
from boardgames.forms import BoardgameForm
from conferences.models import Zosia
from users.models import UserPreferences


@login_required
@require_http_methods(['GET'])
def index(request):
    boardgames = Boardgame.objects.all().annotate(votes=Count('boardgame_votes')).order_by('-votes')

    try:
        current_zosia = Zosia.objects.find_active()
        preferences = UserPreferences.objects.get(
            zosia=current_zosia, user=request.user)
    except (Zosia.DoesNotExist, UserPreferences.DoesNotExist):
        ctx = {'boardgames': boardgames}
    else:
        paid = preferences.payment_accepted
        ctx = {'boardgames': boardgames,
               'paid': paid}
    return render(request, 'boardgames/index.html', ctx)


@login_required
@require_http_methods(['GET', 'POST'])
def my_boardgames(request):
    user_boardgames = Boardgame.objects.filter(user=request.user).annotate(votes=Count('boardgame_votes')).order_by('-votes')
    can_add = user_boardgames.count() < 3
    ctx = {'user_boardgames': user_boardgames,
           'can_add': can_add}
    return render(request, 'boardgames/my_boardgames.html', ctx)


def validate_url(url):
    url_pattern = r'(https://)?boardgamegeek.com/boardgame/\d{1,6}(/[0-9a-z-]+)?'
    return re.match(url_pattern, url)


def get_name(request, url):
    boargamegeek_html = urlopen(url).read()
    title_str = '<title>'
    encoding = "utf-8"
    title_bytes = bytearray(title_str, encoding)
    start_index = boargamegeek_html.find(title_bytes)
    start_index += len(title_str)
    end_index = boargamegeek_html.find(
        bytearray(' |', encoding), start_index)
    name_bytes = boargamegeek_html[start_index: end_index]
    name_str = name_bytes.decode(encoding)
    return name_str


@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    user_boardgames = Boardgame.objects.filter(user=request.user)
    ctx = {'form': BoardgameForm(request.POST or None)}

    if request.method == 'POST':
        if ctx['form'].is_valid() and user_boardgames.count() < 3:
            new_url = ctx['form'].cleaned_data['url']
            if Boardgame.objects.filter(url=new_url).exists():
                messages.error(
                    request, _("This boardgame has been already added"))
            elif not validate_url(new_url):
                messages.error(request, _("This is not a valid boardgame url"))
            else:
                name = get_name(request, new_url)
                if name == "BoardGameGeek":
                    messages.error(request, _(
                        "This is not a valid boardgame url"))
                else:
                    boardgame = Boardgame(
                        name=name, user=request.user, url=new_url)
                    boardgame.save()
                    return redirect('my_boardgames')
        else:
            messages.error(request, _("Error adding boardgame"))

    return render(request, 'boardgames/create.html', ctx)


@login_required
@require_http_methods(['GET'])
def vote(request):
    votes = Vote.objects.filter(
        user=request.user).values_list('boardgame', flat=True)
    ctx = {'boardgames': Boardgame.objects.all(),
           'user_voted': list(votes)}
    return render(request, 'boardgames/vote.html', ctx)


@staff_member_required
@require_http_methods(['POST'])
def vote_edit(request):
    new_ids = json.loads(request.POST.get('new_ids'))

    if len(new_ids) > 3:
        return HttpResponseBadRequest(
            '<h1>Bad request(400)</h1>'
            'Everyone can vote only for up to three boardgames',
            content_type='text/html'
        )

    boardgames = Boardgame.objects.filter(pk__in=new_ids)

    newVotes = list()
    for boardgame in boardgames:
        newVotes.append(Vote(user=request.user, boardgame=boardgame))

    Vote.objects.filter(user=request.user).delete()
    Vote.objects.bulk_create(newVotes)

    return JsonResponse({'new_ids': new_ids})


@staff_member_required
@require_http_methods(['GET'])
def accept(request):
    boardgames = Boardgame.objects.all()
    boardgames = sorted(boardgames, key=lambda x: x.accepted, reverse=True)
    ctx = {'boardgames': boardgames}
    return render(request, 'boardgames/accept.html', ctx)


def toggle_accepted(boardgame_id):
    boardgame = get_object_or_404(Boardgame, pk=boardgame_id)
    boardgame.toggle_accepted()
    boardgame.save()


@staff_member_required
@require_http_methods(['POST'])
def accept_edit(request):
    accepted = Boardgame.objects.filter(
        accepted=True).values_list('id', flat=True)
    old_ids = list(accepted)
    new_ids = json.loads(request.POST.get('new_ids'))
    common_ids = [x for x in old_ids if x in new_ids]
    old_ids = [x for x in old_ids if x not in common_ids]
    new_ids = [x for x in new_ids if x not in common_ids]
    for x in old_ids:
        toggle_accepted(x)
    for x in new_ids:
        toggle_accepted(x)
    return JsonResponse({'old_ids': old_ids, 'new_ids': new_ids})


@staff_member_required
@require_http_methods(['POST'])
def boardgame_delete(request):
    boardgame_id = request.POST.get('boardgame_id')
    boardgame = get_object_or_404(Boardgame, pk=boardgame_id)
    boardgame.delete()
    return JsonResponse({'msg': "Deleted the boardgame: {}".format(
        escape(boardgame))})
