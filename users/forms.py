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

    def save(self):
        data = self.cleaned_data

        user = User(
            email=data['email'],
            username=data['username'],
        )
        user.set_password(data['password'])
        user.is_active = False
        user.save()

        return user
