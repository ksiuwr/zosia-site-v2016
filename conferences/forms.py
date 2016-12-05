from django.forms import ModelForm

from .models import UserPreferences, Zosia, Bus
from users.models import Organization


class UserPreferencesForm(ModelForm):
    class Meta:
        model = UserPreferences
        exclude = ['user', 'zosia', 'payment_accepted', 'bonus_minutes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organization'].queryset = Organization.objects.filter(accepted=True)
        self.fields['bus'].queryset = Bus.objects.filter(zosia=Zosia.objects.find_active())

    def call(self, zosia, user):
        user_preferences = self.save(commit=False)
        user_preferences.user = user
        user_preferences.zosia = zosia
        user_preferences.save()
        return user_preferences
