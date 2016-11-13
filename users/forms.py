from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }
