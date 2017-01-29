from django import forms
from questions.models import QA


class QAForm(forms.ModelForm):
    class Meta:
        model = QA
        fields = '__all__'
