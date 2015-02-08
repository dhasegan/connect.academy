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

class ChangeEmailForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required= True, widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(ChangeEmailForm,self).clean()
        errors = []
        try:
            emailID, domain = cleaned_data['email'].split('@')
            university = University.objects.get(domains__name=domain)
            cleaned_data['is_alumnus'] = False
            if Domain.objects.get(name=domain).domain_type == DOMAIN_TYPE_ALUMNI:
                cleaned_data['is_alumnus'] = True
        except Exception as e:
            errors.append(forms.ValidationError("The e-mail address you entered is not valid."))
            print e
        if errors:
            raise forms.ValidationError(errors)
        return cleaned_data

class EditSummaryForm(forms.Form):
	summary = forms.CharField(max_length=300, required=False)

class ProfilePictureForm(forms.Form):
	picture = forms.ImageField()