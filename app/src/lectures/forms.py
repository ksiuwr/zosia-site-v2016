from django import forms

from lectures.models import Lecture, Schedule


class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['title', 'abstract', 'lecture_type', 'duration', 'requests', 'events']
        widgets = {
            'abstract': forms.Textarea,
            'requests': forms.Textarea,
            'events': forms.Textarea
        }


class LectureAdminForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['author', 'person_type', 'description', 'title', 'abstract', 'lecture_type',
                  'duration', 'requests', 'events', 'accepted']
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
        fields = ['content']
