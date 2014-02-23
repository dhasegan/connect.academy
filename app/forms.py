from django import forms

from app.course_info import *
from app.models import *

class VoteCourseForm(forms.Form):
    course_id = forms.CharField()
    rating_value = forms.CharField()
    rating_type = forms.CharField()
    url = forms.CharField()
    profname = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super(VoteCourseForm, self).clean()

        try:
            rvalue = float(cleaned_data.get("rating_value"))
        except:
            raise forms.ValidationError("Rating value is not valid!")
        cleaned_data['rating_value'] = rvalue

        rtype = cleaned_data.get("rating_type")
        if not rtype in dict(RATING_TYPES):
            raise forms.ValidationError("Not a valid rating type!")

        courses = Course.objects.filter(id=cleaned_data.get("course_id"))
        if len(courses) != 1:
            raise forms.ValidationError("Not a valid number of courses with this course_id!")
        cleaned_data['course'] = courses[0]

        if rtype == PROFESSOR_R:
            if not 'profname' in cleaned_data:
                raise forms.ValidationError("There is no professor name for the form!")
            profs = Professor.objects.filter(name=cleaned_data['profname'])
            if len(profs) != 1:
                raise forms.ValidationError("Not a valid number of professors with this professor name!")
            cleaned_data['prof'] = profs[0]

        return cleaned_data

class SubmitCommentForm(forms.Form):
    course_id = forms.CharField()
    comment = forms.CharField()
    url = forms.CharField()

    def clean(self):
        cleaned_data = super(SubmitCommentForm, self).clean()

        courses = Course.objects.filter(id=cleaned_data.get("course_id"))
        if len(courses) != 1:
            raise forms.ValidationError("Not a valid number of courses with this course_id!")
        cleaned_data['course'] = courses[0]

        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()