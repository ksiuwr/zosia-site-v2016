from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import UserPreferences, Zosia, Bus
from users.models import Organization


class UserPreferencesForm(forms.ModelForm):
    # NOTE: I'm not sure if that's how it should be:
    DEPENDENCIES = [
        # This means you need to check accomodation_1 before you can check dinner_1
        ['accomodation_day_1', 'dinner_1'],
        # This means you need to check accomodation_2 before you can check breakfast2 or dinner_2
        ['accomodation_day_2', 'breakfast_2', 'dinner_2'],
        ['accomodation_day_3', 'breakfast_3', 'dinner_3']
    ]

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

    def clean(self):
        cleaned_data = super().clean()

        def _pays_for(d):
            return cleaned_data.get(d, False)

        groups = self.DEPENDENCIES
        errs = []

        for day in groups:
            deps = list(map(_pays_for, day[1:]))
            if any(deps) and not _pays_for(day[0]):
                errs.append(forms.ValidationError(_('You need to check %(req) before you can check %(dep)'),
                                                  code='invalid',
                                                  params={'field': day[0],
                                                          'dep': day[1:][deps.index(True)]}))

        if len(errs) > 0:
            raise forms.ValidationError(errs)

    def disable(self):
        for field in self.fields:
            if field not in ['contact', 'shirt_size', 'shirt_type']:
                self.fields[field].disabled = True
