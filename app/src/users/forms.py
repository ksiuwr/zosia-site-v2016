from django import forms
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe

from .actions import SendActivationEmail, SendEmailToAll
from .models import User, Organization

GROUPS = (
        ('pick', 'Pick users'),
        ('all_Users', 'All users'),
        ('staff', 'Staff'),
        ('active', 'Active'),
        ('inactive', 'Don\'t activate their account yet'),
        ('registered', 'Registered to zosia'),
        ('payed', 'Payed for zosia'),
        ('not_Payed', 'Didn`t pay for zosia'),
    )


class MailForm(forms.Form):
    subject = forms.CharField()
    text = forms.CharField(widget=forms.Textarea)
    select_groups = forms.ChoiceField(choices=GROUPS)
    pick = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(), to_field_name="email", required=False)
    all_Users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(), to_field_name="email", required=False)
    staff = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_staff=True),
        to_field_name="email", required=False)
    active = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        to_field_name="email", required=False)
    inactive = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=False),
        to_field_name="email", required=False)
    registered = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(userpreferences__isnull=False).distinct(),
        to_field_name="email", required=False)
    payed = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(userpreferences__payment_accepted=True).distinct(),
        to_field_name="email", required=False)
    not_Payed = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(userpreferences__payment_accepted=False).distinct(),
        to_field_name="email", required=False)

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        self.fields["all_Users"].initial = (
            User.objects.all().values_list('email', flat=True)
        )
        self.fields["staff"].initial = (
            User.objects.filter(is_staff=True).values_list('email', flat=True)
        )
        self.fields["active"].initial = (
            User.objects.filter(is_active=True).values_list('email', flat=True)
        )
        self.fields["inactive"].initial = (
            User.objects.filter(is_active=False).values_list('email', flat=True)
        )
        self.fields["registered"].initial = (
            User.objects.filter(userpreferences__isnull=False).distinct()
            .values_list('email', flat=True)
        )
        self.fields["payed"].initial = (
            User.objects.filter(userpreferences__payment_accepted=True).distinct()
            .values_list('email', flat=True)
        )
        self.fields["not_Payed"].initial = (
            User.objects.filter(userpreferences__payment_accepted=False).distinct()
            .values_list('email', flat=True)
        )

    def receivers(self):
        return self.cleaned_data[self.cleaned_data["select_groups"]]

    def send_mail(self):
        users = self.receivers()
        SendEmailToAll(users=users).call(
            self.cleaned_data['subject'],
            self.cleaned_data['text']
        )
        print(users)


class UserForm(UserCreationForm):
    privacy_consent = forms.BooleanField(
        required=True
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        label = (
            f'I agree to <a href="{reverse("terms_and_conditions")}">'
            f'Terms & Conditions</a> and the '
            f'<a href="{reverse("privacy_policy")}">Privacy Policy</a>'
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
