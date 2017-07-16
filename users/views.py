from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.tokens import default_token_generator

from . import forms
from .actions import ActivateUser
from conferences.models import Zosia, UserPreferences


# Create your views here.
@login_required
@require_http_methods(['GET'])
def profile(request):
    current_zosia = Zosia.objects.find_active()
    user_preferences = UserPreferences.objects.select_related(
        'bus', 'zosia').filter(user=request.user)

    current_prefs = user_preferences.filter(zosia=current_zosia).first()
    all_prefs = user_preferences.exclude(zosia=current_zosia).values_list(
        'zosia', flat=True)

    ctx = {
        'zosia': current_zosia,
        'current_prefs': current_prefs,
        'all_prefs': all_prefs
    }
    return render(request, 'users/profile.html', ctx)


@require_http_methods(['GET', 'POST'])
def signup(request):
    form = forms.UserForm(request.POST or None)
    ctx = {
        'form': form,
    }

    if request.method == 'POST':
        if form.is_valid():
            form.save(request)
            return render(request, 'users/signup_done.html', ctx)

    return render(request, 'users/signup.html', ctx)


@login_required
@require_http_methods(['GET', 'POST'])
def account_edit(request):
    form = forms.EditUserForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('accounts_profile')
    ctx = {'form': form}
    return render(request, 'users/signup.html', ctx)


@require_http_methods(['GET', 'POST'])
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
