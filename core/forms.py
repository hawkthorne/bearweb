from django import forms
from django.core.mail import send_mail


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
