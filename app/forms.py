from django import forms


class NewSubscriberForm(forms.Form):
	name = forms.CharField(max_length=100, required = True)
	email = forms.EmailField(max_length=100, required = True)