from django import forms

from app.models import *


class LoginForm(forms.Form):
    user_auth = forms.CharField(required=True)
    password = forms.CharField(required=True)


class SignupForm(forms.Form):
    fname = forms.CharField()
    lname = forms.CharField()
    email = forms.EmailField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirmation = forms.CharField(widget=forms.PasswordInput())  # password confirmation field
    is_instructor = forms.BooleanField(required=False)

    class Meta:
        model = jUser

    def clean(self):
        cleaned_data = super(SignupForm,self).clean()

        email = cleaned_data['email']
        username = cleaned_data['username']
        password = cleaned_data['password']
        password_confirmation = cleaned_data['password_confirmation']

        errors = []

        if jUser.objects.filter(username = username).count() > 0:
            errors.append(forms.ValidationError("A user with that username already exists."))
        
        if jUser.objects.filter(email = email).count() > 0:
            errors.append(forms.ValidationError("A user with that e-mail address already exists."))
        
        if password != password_confirmation:
            errors.append(forms.ValidationError("Passwords do not match."))
        
        if len(password) < 6:
            errors.append(forms.ValidationError("Password is too short."))
        
        try:
            emailID, domain = email.split('@')
        except ValueError:
            errors.append(forms.ValidationError("The e-mail address you entered is not valid."))

        universities = University.objects.filter(domains__name=domain)
        if not universities:
            errors.append(forms.ValidationError("Sorry, we don't have any university with the domain of your \
                e-mail address. Please check if you made any errors or come back soon."))

        if errors:
            raise forms.ValidationError(errors)

        cleaned_data['university'] = universities[0]
        return cleaned_data





class EmailConfirmationForm(forms.Form):
    email = forms.EmailField()

    def clean(self):
        cleaned_data = super(EmailConfirmationForm, self).clean()
        email = cleaned_data.get("email")   
        errors = []
        
        if not email:
            errors.append(forms.ValidationError("No e-mail address provided."))
        if jUser.objects.filter(email=email).count() > 0:
            errors.append(forms.ValidationError("A user with that e-mail address already exists."))

        try:
            emailID, domain = email.split('@')
        except ValueError:
            errors.append(forms.ValidationError("The e-mail address you entered is not valid."))

        universities = University.objects.filter(domains__name=domain)
        if not universities:
            errors.append(forms.ValidationError("Sorry, we don't have any university with the domain of your \
                e-mail address. Please check if you made any errors or come back soon."))

        if errors:
            raise forms.ValidationError(errors)

        cleaned_data['university'] = universities[0]
        return cleaned_data