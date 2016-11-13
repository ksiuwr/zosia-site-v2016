from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user


# Create your views here.
@login_required
def profile(request):
    ctx = {
        'user' : get_user(request)
    }
    return render(request, 'users/profile.html', ctx)
