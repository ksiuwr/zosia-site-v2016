from django import forms
from .models import Boardgame


class BoardgameForm(forms.ModelForm):
    class Meta:
        model = Boardgame
        exclude = ['votes_amount', 'state']


# class BoardgameVote(forms.ModelForm):
#     boardgame = forms.ModelChoiceField(queryset=Boargame.objects.all(), required=False, help_text="Boardgame")
#     class Meta:
#         model = Boardgame