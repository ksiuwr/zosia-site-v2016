from django import forms

from conferences.models import Bus, Place, Zosia


class SplitDateTimePickerField(forms.SplitDateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = forms.SplitDateTimeWidget(date_attrs={"class": "datepicker"},
                                                     time_attrs={"class": "timepicker"})
        super().__init__(*args, **kwargs)


class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        exclude = []
        field_classes = {
            "departure_time": SplitDateTimePickerField
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        exclude = []

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
