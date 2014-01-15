from django import forms

from .models import Game


class LoveForm(forms.Form):
    lovefile = forms.FileField(required=True)
    version = forms.CharField(required=True)


class GameForm(forms.ModelForm):
    class Meta:
        fields = ['name', 'framework', 'public']
        model = Game
        widgets = {
            'public': forms.RadioSelect(attrs={'title': 'FOO'})
        }
