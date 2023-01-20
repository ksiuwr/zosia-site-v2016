from django import forms
from organizers.models import OrganizerContact


class OgranizerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        organizer = kwargs.get('instance')
        if(organizer is not None):
            self.fields.pop('user')

    class Meta:
        model = OrganizerContact
        fields = '__all__'
