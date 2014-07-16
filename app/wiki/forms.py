from django import forms
from django.template.defaultfilters import filesizeformat

from app.models import *



#The form required for submitting a create/change request to a course's Wiki
class WikiPageForm(forms.Form):
    content = forms.CharField(required=True)

