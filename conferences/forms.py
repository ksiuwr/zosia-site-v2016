from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import UserPreferences, Zosia, Bus
from users.models import Organization


def bus_queryset(**kwargs):
        bus_queryset = Bus.objects.find_with_free_places(Zosia.objects.find_active())
        if 'instance' in kwargs:
            bus_queryset = bus_queryset | Bus.objects.filter(userpreferences=kwargs['instance'])
        return bus_queryset


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

    # Yes, it's required by default. But it's insane - better be verbose than misunderstood.
    accepted = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organization'].queryset = Organization.objects.filter(accepted=True)
        self.fields['bus'].queryset = bus_queryset(**kwargs)

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


class UserPreferencesAdminForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        exclude = [
            'user',
            'zosia',
            'organization',
            'accomodation_day_1',
            'dinner_1',
            'accomodation_day_2',
            'dinner_2',
            'breakfast_2',
            'accomodation_day_3',
            'dinner_3',
            'breakfast_3',
            'breakfast_4',
            'vegetarian'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bus'].queryset = bus_queryset(**kwargs)
        # NOTE: Seems like it's not working?
        self.fields['contact'].disabled = True
