from django import forms
from .models import Lecture


class LectureForm(forms.ModelForm):

    class Meta:
        model = Lecture
        fields = ['info', 'title', 'abstract', 'duration', 'lecture_type',
                  'person_type']


class LectureAdminForm(forms.ModelForm):
    class Meta:
        model = Lecture
        exclude = ['zosia', 'create_date', 'order']
