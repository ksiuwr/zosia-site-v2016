from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import UserCreationForm
from django import forms

from .actions import SendActivationEmail
from .models import User


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def save(self, request):
        user = super().save(commit=False)
        user.is_active = False
        user.save()

        SendActivationEmail(
            user=user,
            site=get_current_site(request),
            token_generator=default_token_generator,
            use_https=request.is_secure(),
        ).call()

        self.user = user
        return user
