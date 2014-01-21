from django import forms
from django.forms import widgets

from .models import Game


class LoveForm(forms.Form):
    lovefile = forms.FileField(required=True)
    version = forms.CharField(required=True)


class ClearableImageInput(widgets.ClearableFileInput):
    template_with_initial = ('%(initial)s<br />%(clear_template)s'
                             '<br />%(input_text)s: %(input)s')
    url_markup_template = '<img src="{0}"/>'


class UpdateGameForm(forms.ModelForm):
    class Meta:
        fields = ['name', 'public', 'icon', 'splash']
        model = Game
        widgets = {
            'public': forms.RadioSelect(attrs={'title': 'FOO'}),
            'icon': ClearableImageInput,
            'splash': ClearableImageInput,
        }


class GameForm(forms.ModelForm):
    class Meta:
        fields = ['name', 'framework', 'public']
        model = Game
        widgets = {
            'public': forms.RadioSelect(attrs={'title': 'FOO'})
        }
