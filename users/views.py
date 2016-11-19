from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator

from . import forms
from .actions import ActivateUser


# Create your views here.
@login_required
def profile(request):
    return render(request, 'users/profile.html')


def signup(request):
    form = forms.UserForm(request.POST or None)
    ctx = {
        'form': form,
    }

    if request.method == 'POST':
        if form.is_valid():
            user = form.save(request)
            return render(request, 'users/signup_done.html', ctx)

    return render(request, 'users/signup.html', ctx)


def activate(request, uidb64, token):
    action = ActivateUser(
        token_generator=default_token_generator,
        uidb64=uidb64,
        token=token,
    )

    if action.is_valid():
        action.call()
        login(request, action.user)
        return redirect('index')

    ctx = {
        'user': action.user,
    }
    return render(request, 'users/activate.html', ctx)
