from django import forms
from .models import Lecture, Schedule


class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['title', 'abstract', 'duration', 'info', 'lecture_type',
                  'person_type']


class LectureAdminForm(forms.ModelForm):
    field_order = ['title', 'abstract', 'duration', 'lecture_type',
                   'author', 'person_type', 'description',
                   'accepted', 'info']

    class Meta:
        model = Lecture
        exclude = ['zosia', 'create_date', 'priority']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['accepted'].checkbox = True


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        exclude = ['zosia']
