from django import forms

from app.models import *


class LoginForm(forms.Form):
    user_auth = forms.CharField(required=True)
    password = forms.CharField(required=True)


class SignupForm(forms.Form):
    username = forms.CharField(max_length=30, required=True)
    fname = forms.CharField(max_length=30)
    lname = forms.CharField(max_length=30)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirmation = forms.CharField(widget=forms.PasswordInput())  # password confirmation field
    is_professor = forms.BooleanField(required=False)

    #class Meta: # Don't ask django to check agains jUser, because fake users with that email might exist
    #    model = jUser

    def clean(self):
        cleaned_data = super(SignupForm,self).clean()

        email = cleaned_data.get('email')
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        errors = []

        if jUser.objects.filter(username = username, is_fake=False ).count() > 0:
            errors.append(forms.ValidationError("A user with that username already exists. Choose another one"))
        
        if jUser.objects.filter(email = email, is_fake = False).count() > 0:
            errors.append(forms.ValidationError("A user with that e-mail address already exists. Choose another one"))
        
        if password != password_confirmation:
            errors.append(forms.ValidationError("Passwords do not match. Please try again"))
        
        if len(password) < 6:
            errors.append(forms.ValidationError("Password is too short. Please enter at least 6 characters"))
        
        if not email:
            if errors:
                raise forms.ValidationError(errors)
            return cleaned_data

        try:
            emailID, domain = email.split('@')
            university = University.objects.get(domains__name=domain)
            cleaned_data['is_alumnus'] = False
            if Domain.objects.get(name=domain).domain_type == DOMAIN_TYPE_ALUMNI:
                cleaned_data['is_alumnus'] = True
        except ValueError:
            errors.append(forms.ValidationError("The e-mail address you entered is not valid."))
        except University.DoesNotExist:
            errors.append(forms.ValidationError("Sorry, we don't have any university with the domain of your \
                e-mail address. Please check if you made any errors or come back soon."))
        except Domain.DoesNotExist:
            errors.append(forms.ValidationError("The e-mail address you entered is not valid."))

        if errors:
            raise forms.ValidationError(errors)

        if jUser.objects.filter(email = email, is_fake = True).count() > 0:
            cleaned_data['has_fake_account'] = True
        else:
            cleaned_data['has_fake_account'] = False

        cleaned_data['university'] = university

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


class EmailPasswordResetForm(forms.Form):
    email = forms.EmailField()

    def clean(self):
        cleaned_data = super(EmailPasswordResetForm, self).clean()
        email = cleaned_data.get("email")

        errors = []

        try:
            cleaned_data['user'] = jUser.objects.get(email = email)
        except Exception:
            errors.append(forms.ValidationError("A user with that e-mail address does not exist. Please register if you don't have an account."))

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data

class NewPasswordForm(forms.Form):
    new_pass = forms.CharField(widget = forms.PasswordInput(), required = True)
    confirm_new_pass = forms.CharField(widget = forms.PasswordInput(), required = True)

    def clean(self):
        cleaned_data = super(NewPasswordForm, self).clean()
        errors = []
        try:
            new_pass = self.cleaned_data["new_pass"]
            confirm_new_pass = self.cleaned_data["confirm_new_pass"]
        except Exception:
            errors.append(forms.ValidationError("Please fill out all required fields"))


        if new_pass != confirm_new_pass:
            errors.append(forms.ValidationError("Passwords do not match."))
        
        if len(new_pass) < 6:
            errors.append(forms.ValidationError("Password is too short."))

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data