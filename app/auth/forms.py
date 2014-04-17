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

    def clean(self):
        cleaned_data = super(EmailConfirmationForm, self).clean()

        email = cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("No e-mail address provided.")
        if jUser.objects.filter(email=email).count() > 0:
            raise forms.ValidationError("A user with that e-mail address already exists.")

        emailID, domain = email.split('@')
        universities = University.objects.filter(domains__name=domain)
        if not universities:
            raise forms.ValidationError("Sorry, we don't have any university with the domain of your \
                e-mail address. Please check if you made any errors or come back soon.")

        cleaned_data['university'] = universities[0]
        return cleaned_data