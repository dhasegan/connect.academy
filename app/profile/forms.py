from django import forms

from app.course_info import *
from app.models import *

class EmailConfirmationForm(forms.Form):
    email = forms.EmailField()

class ChangePasswordForm(forms.Form):
    old_pass = forms.CharField(required = True ,widget=forms.PasswordInput())
    new_pass = forms.CharField(required = True ,widget=forms.PasswordInput())
    confirm_new_pass = forms.CharField(required = True , widget=forms.PasswordInput())

class ChangeUsernameForm(forms.Form):
    new_username = forms.CharField(required = True)
    password = forms.CharField(required=True,widget= forms.PasswordInput())

class ChangeNameForm(forms.Form):
    new_fname = forms.CharField(required= True)
    new_lname = forms.CharField(required= True) # maybe we can omit the required = True of this field ? 
    password = forms.CharField(required=True,widget=forms.PasswordInput())