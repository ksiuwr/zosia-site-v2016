from django import forms
from django.utils.translation import ugettext_lazy as _

from conferences.models import Bus, UserPreferences, Zosia
from conferences.widgets import OrgSelectWithAjaxAdd
from users.models import Organization
from utils.constants import PAYMENT_GROUPS


class SplitDateTimePickerField(forms.SplitDateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = forms.SplitDateTimeWidget(date_attrs={"class": "datepicker"},
                                                     time_attrs={"class": "timepicker"})
        super().__init__(*args, **kwargs)


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

    # NOTE: In hindsight, this sucks.
    # Forget about this whitelist after adding fields
    # and weird stuff happens when someone tries to update preferences.
    CAN_CHANGE_AFTER_PAYMENT_ACCEPTED = ['contact', 'shirt_size', 'shirt_type']

    class Meta(UserPreferencesWithOrgForm.Meta):
        model = UserPreferences
        exclude = ['user', 'zosia', 'payment_accepted', 'bonus_minutes']

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

        errs = []

        for accommodation, meals in PAYMENT_GROUPS.items():
            chosen = [_pays_for(m) for m in meals]

            if any(chosen) and not _pays_for(accommodation):
                errs.append(
                    forms.ValidationError(_('You need to check %(req) before you can check %(dep)'),
                                          code='invalid',
                                          params={'req': accommodation,
                                                  'dep': meals[chosen.index(True)]})
                )

        if len(errs) > 0:
            raise forms.ValidationError(errs)

    def disable(self):
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
            'accommodation_day_1',
            'dinner_day_1',
            'accommodation_day_2',
            'dinner_day_2',
            'breakfast_day_2',
            'accommodation_day_3',
            'dinner_day_3',
            'breakfast_day_3',
            'breakfast_day_4',
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
        field_classes = {
            "departure_time": SplitDateTimePickerField
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ZosiaForm(forms.ModelForm):
    class Meta:
        model = Zosia
        exclude = []
        field_classes = {
            "registration_start": SplitDateTimePickerField,
            "registration_end": SplitDateTimePickerField,
            "rooming_start": SplitDateTimePickerField,
            "rooming_end": SplitDateTimePickerField,
            "lecture_registration_start": SplitDateTimePickerField,
            "lecture_registration_end": SplitDateTimePickerField
        }

    def __init__(self, *args, **kwargs):
        super(ZosiaForm, self).__init__(*args, **kwargs)
