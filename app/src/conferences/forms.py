from django import forms

from conferences.models import Place, Transport, Zosia


class SplitDateTimePickerField(forms.SplitDateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = forms.SplitDateTimeWidget(date_attrs={"class": "datepicker"},
                                                     time_attrs={"class": "timepicker"})
        super().__init__(*args, **kwargs)
        self.help_text = "Provide date and time in <b>UTC</b> time zone!"


class TransportForm(forms.ModelForm):
    class Meta:
        model = Transport
        fields = '__all__'
        field_classes = {
            "departure_time": SplitDateTimePickerField
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PlaceForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Place

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ZosiaForm(forms.ModelForm):
    early_registration_start = SplitDateTimePickerField(required=False)

    class Meta:
        model = Zosia
        fields = '__all__'
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
