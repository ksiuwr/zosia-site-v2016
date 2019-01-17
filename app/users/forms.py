from django import forms
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.utils.safestring import mark_safe


from .actions import SendActivationEmail
from .models import User, Organization

_CONSENT_LABEL = 'I agree to <a href="{}">Terms & Conditions</a> and the <a href="{}">Privacy Policy</a>'.format(
    # reverse('conferences:terms_and_conditions'),
    # reverse('conferences:privacy_policy')
    "url_to_terms_and_conditions",
    "url_to_privacy_policy"
)


class UserForm(UserCreationForm):
    privacy_consent = forms.BooleanField(
        label=mark_safe(_CONSENT_LABEL),
        required=True
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

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


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'accepted']
