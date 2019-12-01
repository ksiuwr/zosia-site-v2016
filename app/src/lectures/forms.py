from django import forms

from lectures.models import Lecture, Schedule


class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['title', 'abstract', 'duration', 'lecture_type', 'requests', 'events']
        widgets = {
            'abstract': forms.Textarea,
            'requests': forms.Textarea,
            'events': forms.Textarea
        }


class LectureAdminForm(forms.ModelForm):
    field_order = ['author', 'title', 'abstract', 'duration', 'lecture_type', 'person_type',
                   'description', 'requests', 'events', 'accepted']

    class Meta:
        model = Lecture
        exclude = ['zosia', 'create_date', 'priority']
        widgets = {
            'abstract': forms.Textarea,
            'description': forms.Textarea,
            'requests': forms.Textarea,
            'events': forms.Textarea
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['accepted'].checkbox = True


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        exclude = ['zosia']
