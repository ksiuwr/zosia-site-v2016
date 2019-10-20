from django import forms
from django.utils.translation import ugettext_lazy as _

from users.models import Organization
from .models import Bus, UserPreferences, Zosia
from .widgets import OrgSelectWithAjaxAdd


class DateWidget(forms.TextInput):
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update({'class': 'datepicker'})
        super(DateWidget, self).__init__(attrs)


class UserPreferencesWithBusForm(forms.ModelForm):
    def bus_queryset(self, instance=None):
        bus_queryset = Bus.objects.find_with_free_places(Zosia.objects.find_active())
        if instance is not None:
            bus_queryset = bus_queryset | Bus.objects.filter(userpreferences=instance)
        return bus_queryset.distinct()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bus'].queryset = self.bus_queryset(kwargs.get('instance'))


class UserPreferencesWithOrgForm(UserPreferencesWithBusForm):
    class Meta:
        widgets = {'organization': OrgSelectWithAjaxAdd}

    def org_queryset(self, user):
        org_queryset = Organization.objects.filter(accepted=True)
        org_queryset = org_queryset | Organization.objects.filter(user=user)
        return org_queryset

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        org_form = self.fields['organization']
        org_form.queryset = self.org_queryset(user)


class UserPreferencesForm(UserPreferencesWithOrgForm):
    use_required_attribute = False
    # NOTE: I'm not sure if that's how it should be:
    DEPENDENCIES = [
        # This means you need to check accomodation_1 before you can check dinner_1
        ['accomodation_day_1', 'dinner_1'],
        # This means you need to check accomodation_2 before you can check breakfast2 or dinner_2
        ['accomodation_day_2', 'breakfast_2', 'dinner_2'],
        ['accomodation_day_3', 'breakfast_3', 'dinner_3']
    ]

    # NOTE: In hindsight, this sucks.
    # Forget about this whitelist after adding fields
    # and weird stuff happens when someone tries to update preferences.
    CAN_CHANGE_AFTER_PAYMENT_ACCEPTED = ['contact', 'shirt_size', 'shirt_type']

    class Meta(UserPreferencesWithOrgForm.Meta):
        model = UserPreferences
        exclude = ['user', 'zosia', 'payment_accepted', 'bonus_minutes']

    # Yes, it's required by default. But it's insane - better be verbose than misunderstood.
    accepted = forms.BooleanField(required=True)

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.user = user

    def call(self, zosia):
        user_preferences = self.save(commit=False)
        user_preferences.user = self.user
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
                errs.append(
                    forms.ValidationError(_('You need to check %(req) before you can check %(dep)'),
                                          code='invalid',
                                          params={'field': day[0],
                                                  'dep': day[1:][deps.index(True)]}))

        if len(errs) > 0:
            raise forms.ValidationError(errs)

    def disable(self):
        self.fields['accepted'].initial = True
        for field in self.fields:
            if field not in self.CAN_CHANGE_AFTER_PAYMENT_ACCEPTED:
                self.fields[field].disabled = True


class UserPreferencesAdminForm(UserPreferencesWithBusForm):
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
        # NOTE: Seems like it's not working?
        # Probably because JS overwrites HTML attr. Argh.
        self.fields['contact'].disabled = True


class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        exclude = []
        widgets = {
            'time': DateWidget,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ZosiaForm(forms.ModelForm):
    class Meta:
        model = Zosia
        exclude = []
        widgets = {
            'start_date': DateWidget,
            'registration_start': DateWidget,
            'registration_end': DateWidget,
            'rooming_start': DateWidget,
            'rooming_end': DateWidget,
            'lecture_registration_start': DateWidget,
            'lecture_registration_end': DateWidget,
        }

    def __init__(self, *args, **kwargs):
        super(ZosiaForm, self).__init__(*args, **kwargs)
