from django import forms
from sponsors.models import Sponsor


class SponsorForm(forms.ModelForm):
    class Meta:
        model = Sponsor
        fields = '__all__'
