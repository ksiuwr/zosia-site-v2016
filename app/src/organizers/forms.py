from django import forms
from organizers.models import OrganizerContact


class OgraniserForm(forms.ModelForm):
    class Meta:
        model = OrganizerContact
        fields = '__all__'
