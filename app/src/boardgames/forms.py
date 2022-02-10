from django import forms
from django.utils.safestring import mark_safe


class BoardgameForm(forms.Form):
    url = forms.CharField(
        label=mark_safe(
            'Find your boardgame on: <a href="https://boardgamegeek.com/">'
            'boardgamegeek.com</a> and paste the link here'), max_length=200)
