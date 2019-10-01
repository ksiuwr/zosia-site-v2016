from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Boardgame
from .forms import BoardgameForm
# from django.http import HttpResponse

@require_http_methods(['GET'])
def index(request):
    ctx = {'boardgames': Boardgame.objects.all()}
    return render(request, 'boardgames/index.html', ctx)
    # return HttpResponse("Hello, world. You're at the polls index.")


# @login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    ctx = {'form': BoardgameForm(request.POST or None)}

    # POST już po submicie, wpp GET czyli wyświetl formularz
    if request.method == 'POST':
        if ctx['form'].is_valid():
            ctx['form'].save()
            return redirect('boardgames_index')
    return render(request, 'boardgames/create.html', ctx)


def vote(request):
    # CHANGE TO "A" !!!!
    ctx = {'boardgames': Boardgame.objects.filter(state="S")}

    if request.method == 'POST':
        pass
    return render(request, 'boardgames/vote.html', ctx)
