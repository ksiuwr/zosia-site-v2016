from django import forms
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe

from .actions import SendActivationEmail, SendEmailToAll
from .models import User, Organization

class MailForm(forms.Form):
    subject = forms.CharField()
    text = forms.CharField(widget=forms.Textarea)
    def send_mail(self):
        users = User.objects.filter(is_staff=True)
        SendEmailToAll(users=users).call(
            self.cleaned_data['subject'],
            self.cleaned_data['text']
        )
        print (users)


class UserForm(UserCreationForm):
    privacy_consent = forms.BooleanField(
        required=True
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);
        label = 'I agree to <a href="{}">Terms & Conditions</a> and the <a href="{}">Privacy Policy</a>'.format(
                reverse('terms_and_conditions'),
                reverse('privacy_policy')
            )
        privacy_consent = self.fields['privacy_consent'].label = mark_safe(label)

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
