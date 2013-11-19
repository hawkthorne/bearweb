from django import forms
from django.core.mail import send_mail
from dockerindex.models import Repository


ACCESS_CHOICES = (
    ('read', 'Read'),
    ('write', 'Read and Write'),
)


class AccessKeyForm(forms.Form):
    access = forms.ChoiceField(choices=ACCESS_CHOICES, required=True)

    def __init__(self, u, *args, **kwargs):
        super(AccessKeyForm, self).__init__(*args, **kwargs)
        self.fields['repository'] = \
            forms.ModelChoiceField(queryset=Repository.objects.filter(user=u),
                                   empty_label='All Repositories',
                                   required=False)


class ContactForm(forms.Form):
    email = forms.EmailField()
    subject = forms.CharField(max_length=100)
    body = forms.CharField(widget=forms.Textarea)

    def send_email(self):
        subject = self.cleaned_data['subject']
        message = self.cleaned_data['body']
        sender = self.cleaned_data['email']
        recipients = ['contact@stackmachine.com']
        send_mail(subject, message, sender, recipients)
