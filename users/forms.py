from django import forms
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator

from .actions import SendActivationEmail
from .models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

    def save(self, request):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_active = False
        user.save()

        SendActivationEmail(
            user=user,
            site=get_current_site(request),
            token_generator=default_token_generator,
            use_https=request.is_secure(),
        ).call()

        self.user = user
