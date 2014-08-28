from django import forms

from app.models import *


class ChangePasswordForm(forms.Form):
    old_pass = forms.CharField(required=True, widget=forms.PasswordInput())
    new_pass = forms.CharField(required=True, widget=forms.PasswordInput())
    confirm_new_pass = forms.CharField(required=True, widget=forms.PasswordInput())


class ChangeUsernameForm(forms.Form):
    new_username = forms.CharField(max_length=30, required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())


class ChangeNameForm(forms.Form):
    new_fname = forms.CharField(max_length=30, required=True)
    new_lname = forms.CharField(max_length=30, required=True)  # maybe we can omit the required = True of this field ?
    password = forms.CharField(required=True, widget=forms.PasswordInput())

class EditSummaryForm(forms.Form):
	summary = forms.CharField(max_length=300, required=False)

class ProfilePictureForm(forms.Form):
	picture = forms.ImageField()