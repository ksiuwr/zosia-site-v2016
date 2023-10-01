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


MAX_NUMBER_OF_GAMES = 3


@login_required
@require_http_methods(['GET'])
def index(request):
    boardgames = Boardgame.objects.all().annotate(
        votes=Count('boardgame_votes')).order_by('-votes', 'name')

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
    user_boardgames = Boardgame.objects.filter(user=request.user).annotate(
        votes=Count('boardgame_votes')).order_by('-votes', 'name')
    can_add = user_boardgames.count() < MAX_NUMBER_OF_GAMES
    ctx = {'user_boardgames': user_boardgames,
           'can_add': can_add}
    return render(request, 'boardgames/my_boardgames.html', ctx)


def validate_game_url(url: str) -> bool:
    url_pattern = r'(https://)?boardgamegeek.com/boardgame/\d{1,6}(/[0-9a-z-]+)?'
    if re.match(url_pattern, url) is None:
        return False

    if not url.startswith("https://"):
        url = f"https://{url}"

    # Game name should be different then BoardGameGeek
    return get_game_name(url) != "BoardGameGeek"


# TODO: Simplify title detection
def get_game_name(url) -> str:
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


def get_id(url):
    match = re.search(r'(boardgame\/)([0-9]+)', url)
    return match.group(2)


@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    user_boardgames = Boardgame.objects.filter(user=request.user)
    ctx = {'form': BoardgameForm(request.POST or None)}

    if request.method == 'POST':
        if user_boardgames.count() >= MAX_NUMBER_OF_GAMES:
            messages.error(request, _(f"Number of boardgames per account exceeded (max: {MAX_NUMBER_OF_GAMES})."))
        elif ctx['form'].is_valid():
            new_url = ctx['form'].cleaned_data['url']
            if not validate_game_url(new_url):
                messages.error(request, _("This is not a valid boardgame url"))
            else:
                game_id = get_id(new_url)
                # TODO: We should save only game id in the model instead of full URL
                url_part = 'boardgame/' + game_id
                if Boardgame.objects.filter(url__contains=url_part).exists():
                    messages.error(
                        request, _("This boardgame has been already added"))
                else:
                    name = get_game_name(new_url)
                    boardgame = Boardgame(
                        name=name, user=request.user, url=new_url)
                    boardgame.save()
                    return redirect('my_boardgames')
        else:
            messages.error(request, _("Can't add boardgame - form is not valid."))

    return render(request, 'boardgames/create.html', ctx)


@login_required
@require_http_methods(['GET'])
def vote(request):
    votes = Vote.objects.filter(
        user=request.user).values_list('boardgame', flat=True)
    ctx = {'boardgames': Boardgame.objects.all().order_by('name'),
           'user_voted': list(votes)}
    return render(request, 'boardgames/vote.html', ctx)


@login_required
@require_http_methods(['POST'])
def vote_edit(request):
    current_zosia = Zosia.objects.find_active()
    preferences = UserPreferences.objects.get(
        zosia=current_zosia, user=request.user)

    if not preferences.payment_accepted:
        return HttpResponseBadRequest(
            '<h1>Bad request(400)</h1>'
            'To vote for boardgames your payment must be accepted first',
            content_type='text/html'
        )

    new_ids = json.loads(request.POST.get('new_ids'))

    if len(new_ids) > MAX_NUMBER_OF_GAMES:
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


@login_required
@require_http_methods(['POST'])
def boardgame_delete(request):
    boardgame_id = request.POST.get('boardgame_id')
    boardgame = get_object_or_404(Boardgame, pk=boardgame_id)

    if boardgame.user != request.user:
        return HttpResponseBadRequest(
            '<h1>Bad request(400)</h1>'
            "You cannot remove someone else's board game",
            content_type='text/html'
        )

    boardgame.delete()
    return JsonResponse({'msg': "Deleted the boardgame: {}".format(
        escape(boardgame))})
