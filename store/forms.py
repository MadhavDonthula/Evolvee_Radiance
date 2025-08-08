from django import forms

class ContactForm(forms.Form):
    email = forms.EmailField(label='Email')
    full_name = forms.CharField(label='Full Name', max_length=100)
    subject = forms.CharField(label='Subject', max_length=150)
    message = forms.CharField(label='Message', widget=forms.Textarea) 