from django import forms


class LoveForm(forms.Form):
    lovefile = forms.FileField()
