from django import forms
from .models import Lecture, Schedule


class LectureForm(forms.ModelForm):

    class Meta:
        model = Lecture
        fields = ['title', 'abstract', 'duration', 'info', 'lecture_type',
                  'person_type']


class LectureAdminForm(forms.ModelForm):
    class Meta:
        model = Lecture
        exclude = ['zosia', 'create_date', 'order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['accepted'].checkbox = True


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        exclude = ['zosia']
