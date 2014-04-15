from django import forms

from app.models import *


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True)


class SignupForm(forms.Form):
    fname = forms.CharField()
    lname = forms.CharField()
    email = forms.EmailField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirmation = forms.CharField(widget=forms.PasswordInput())  # password confirmation field
    is_instructor = forms.BooleanField(required=False)
    department = forms.IntegerField(required=False)

    class Meta:
        model = jUser


class EmailConfirmationForm(forms.Form):
    email = forms.EmailField()
