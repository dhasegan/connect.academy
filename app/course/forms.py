from django import forms
from django.template.defaultfilters import filesizeformat

from app.models import *


class RateCourseForm(forms.Form):
    course_id = forms.CharField()
    rating_value = forms.CharField()
    rating_type = forms.CharField()
    url = forms.CharField()
    profname = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super(RateCourseForm, self).clean()

        try:
            rvalue = float(cleaned_data.get("rating_value"))
        except:
            raise forms.ValidationError("Rating value is not valid!")
        if not (rvalue >= RATING_MIN and rvalue <= RATING_MAX):
            raise forms.ValidationError("Rating value is not valid!")
        cleaned_data['rating_value'] = rvalue

        rtype = cleaned_data.get("rating_type")
        if rtype not in dict(RATING_TYPES):
            raise forms.ValidationError("Not a valid rating type!")

        courses = Course.objects.filter(id=cleaned_data.get("course_id"))
        if len(courses) != 1:
            raise forms.ValidationError("Not a valid number of courses with this course_id!")
        cleaned_data['course'] = courses[0]

        if rtype == PROFESSOR_R:
            if not 'profname' in cleaned_data:
                raise forms.ValidationError("There is no professor name for the form!")
            profs = jUser.objects.filter(username=cleaned_data['profname'])
            if len(profs) != 1:
                raise forms.ValidationError("Not a valid number of professors with this professor name!")
            cleaned_data['prof'] = profs[0]

        return cleaned_data


class SubmitCommentForm(forms.Form):
    course_id = forms.CharField()
    comment = forms.CharField()
    url = forms.CharField()
    anonymous = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super(SubmitCommentForm, self).clean()

        courses = Course.objects.filter(id=cleaned_data.get("course_id"))
        if len(courses) != 1:
            raise forms.ValidationError("Not a valid number of courses with this course_id!")
        cleaned_data['course'] = courses[0]

        return cleaned_data

class SubmitDocumentForm(forms.Form):
    name = forms.CharField()
    document = forms.FileField()
    description = forms.CharField(required=False)
    course_id = forms.CharField()
    url = forms.CharField()

    def clean(self):
        cleaned_data = super(SubmitDocumentForm, self).clean()

        courses = Course.objects.filter(id=cleaned_data.get("course_id"))
        if len(courses) != 1:
            raise forms.ValidationError("Not a valid number of courses with this course_id!")
        cleaned_data['course'] = courses[0]

        return cleaned_data

    def clean_document(self):
        content = self.cleaned_data['document']
        if content._size > settings.COURSE_DOCUMENT_MAX_UPLOAD_SIZE:
            raise forms.ValidationError( ('Please keep filesize under %s. Current filesize %s')
                % (filesizeformat(settings.COURSE_DOCUMENT_MAX_UPLOAD_SIZE), filesizeformat(content._size)))
        return content

class VoteReviewForm(forms.Form):
    review_id = forms.CharField()
    vote_type = forms.CharField()
    url = forms.CharField()

    def clean(self):
        cleaned_data = super(VoteReviewForm, self).clean()

        reviews = Review.objects.filter(id=cleaned_data.get("review_id"))
        if len(reviews) != 1:
            raise forms.ValidationError("Not a valid number of reviews with this review_id!")
        cleaned_data['review'] = reviews[0]

        return cleaned_data

    def clean_vote_type(self):
        vtype = self.cleaned_data['vote_type']
        if not vtype in ['upvote', 'downvote']:
            raise forms.ValidationError("Wrong vote type!")
        return vtype