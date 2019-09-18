from django.views.decorators.http import require_http_methods
# from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from .models import Boardgame
# from .forms import BlogPostForm
from django.http import HttpResponse

@require_http_methods(['GET'])
def index(request):
    ctx = {'boardgames': Boardgame.objects.all()}
    return render(request, 'boardgames/index.html', ctx)
    # return HttpResponse("Hello, world. You're at the polls index.")

# from django.views.generic import ListView
# from .models import Boardgame


# class BoardgameListView(ListView):
#     model = Boardgame
#     template_name = 'boardgames/index.html'
