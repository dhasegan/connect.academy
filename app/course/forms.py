import hashlib
import random
import os

from django import forms
from django.template.defaultfilters import filesizeformat
from app.models import *


def generateRandomFilename(fileExtension):
    return hashlib.sha256(str(random.randint(0,128))).hexdigest() + fileExtension


class RateCourseForm(forms.Form):
    course_id = forms.CharField()
    rating_value = forms.CharField()
    rating_type = forms.CharField()
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
    comment = forms.CharField(max_length=5000)
    anonymous = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super(SubmitCommentForm, self).clean()

        courses = Course.objects.filter(id=cleaned_data.get("course_id"))
        if len(courses) != 1:
            raise forms.ValidationError("Not a valid number of courses with this course_id!")
        cleaned_data['course'] = courses[0]

        return cleaned_data

class SubmitDocumentForm(forms.Form):
    name = forms.CharField(max_length=200)
    document = forms.FileField()
    topic_id = forms.CharField(required=False)
    description = forms.CharField(max_length=1000, required=False)
    course_id = forms.CharField()
    url = forms.CharField()

    def clean(self):
        cleaned_data = super(SubmitDocumentForm, self).clean()

        courses = Course.objects.filter(id=cleaned_data.get("course_id"))
        if len(courses) != 1:
            raise forms.ValidationError("Not a valid number of courses with this course_id!")
        cleaned_data['course'] = courses[0]

        if cleaned_data['topic_id']:
            topics = CourseTopic.objects.filter(id=cleaned_data['topic_id'], course=cleaned_data["course"])
            if topics: 
                cleaned_data["topic"] = topics[0]
            else:
                raise forms.ValidationError("The selected topic does not belong to this course")
        else:
            cleaned_data["topic"] = None

        return cleaned_data

    def clean_document(self):
        content = self.cleaned_data['document']
        if content._size > settings.COURSE_DOCUMENT_MAX_UPLOAD_SIZE:
            raise forms.ValidationError( ('Please keep filesize under %s. Current filesize %s')
                % (filesizeformat(settings.COURSE_DOCUMENT_MAX_UPLOAD_SIZE), filesizeformat(content._size)))
        _, fileExtension = os.path.splitext(content.name)
        content.name = generateRandomFilename(fileExtension)
        return content

class ResubmitDocumentForm(forms.Form):
    document = forms.FileField()
    doc_id = forms.CharField()

    def clean(self):
        cleaned_data = super(ResubmitDocumentForm, self).clean()

        docs = CourseDocument.objects.filter(id=cleaned_data.get("doc_id"))
        if len(docs) != 1:
            raise forms.ValidationError("Not a valid number of documents with this doc_id!")
        cleaned_data['doc_obj'] = docs[0]

        return cleaned_data

    def clean_document(self):
        content = self.cleaned_data['document']
        if content._size > settings.COURSE_DOCUMENT_MAX_UPLOAD_SIZE:
            raise forms.ValidationError( ('Please keep filesize under %s. Current filesize %s')
                % (filesizeformat(settings.COURSE_DOCUMENT_MAX_UPLOAD_SIZE), filesizeformat(content._size)))
        _, fileExtension = os.path.splitext(content.name)
        content.name = generateRandomFilename(fileExtension)
        return content


class SubmitHomeworkForm(forms.Form):
    course_id = forms.CharField()
    homework_request_id = forms.CharField()
    url = forms.CharField()
    document1 = forms.FileField(required=False)
    document2 = forms.FileField(required=False)
    document3 = forms.FileField(required=False)
    document4 = forms.FileField(required=False)
    document5 = forms.FileField(required=False)
    document6 = forms.FileField(required=False)
    document7 = forms.FileField(required=False)
    document8 = forms.FileField(required=False)
    document9 = forms.FileField(required=False)
    document10 = forms.FileField(required=False)

    def clean(self):
        cleaned_data = super(SubmitHomeworkForm, self).clean()

        courses = Course.objects.filter(id=cleaned_data.get("course_id"))
        if len(courses) != 1:
            raise forms.ValidationError("Not a valid number of courses with this course_id!")
        cleaned_data['course'] = courses[0]

        homework_requests = CourseHomeworkRequest.objects.filter(id=cleaned_data.get("homework_request_id"))
        if len(homework_requests) != 1:
            raise forms.ValidationError("Not a valid number of homework requests with this homeworkRequest_id!")
        hw_req = homework_requests[0]
        cleaned_data['homework_request'] = hw_req

        for idx in range(HOMEWORK_MIN_FILES, hw_req.number_files + 1):
            content = cleaned_data.get('document' + str(idx))
            if content:
                if content._size > settings.COURSE_DOCUMENT_MAX_UPLOAD_SIZE:
                    raise forms.ValidationError( ('Please keep filesize under %s. Current filesize %s')
                        % (filesizeformat(settings.COURSE_DOCUMENT_MAX_UPLOAD_SIZE), filesizeformat(content._size)))
                _, fileExtension = os.path.splitext(content.name)
                content.name = generateRandomFilename(fileExtension)
                cleaned_data['document' + str(idx)] = content

        if not homework_requests[0].course == courses[0]:
            raise forms.ValidationError("Integration error!")

        return cleaned_data

class SubmitHomeworkRequestForm(forms.Form):
    name = forms.CharField(max_length=200)
    description = forms.CharField(max_length=1000, required=False)
    topic_id = forms.CharField(required=False)
    start = forms.DateTimeField(input_formats=settings.VALID_TIME_INPUTS)
    deadline = forms.DateTimeField(input_formats=settings.VALID_TIME_INPUTS)
    timezone = forms.IntegerField()
    nr_files = forms.IntegerField(validators=[MinValueValidator(HOMEWORK_MIN_FILES),
                                              MaxValueValidator(HOMEWORK_MAX_FILES)])
    document = forms.FileField(required=False)
    
    course_id = forms.CharField()

    def clean(self):
        cleaned_data = super(SubmitHomeworkRequestForm, self).clean()

        courses = Course.objects.filter(id=cleaned_data.get("course_id"))
        if len(courses) != 1:
            raise forms.ValidationError("Not a valid number of courses with this course_id!")
        cleaned_data['course'] = courses[0]

        if cleaned_data['topic_id']:
            topics = CourseTopic.objects.filter(id=cleaned_data['topic_id'], course=cleaned_data["course"])
            if topics: 
                cleaned_data["topic"] = topics[0]
            else:
                raise forms.ValidationError("The selected topic does not belong to this course")
        else:
            cleaned_data["topic"] = None
        
        return cleaned_data

    def clean_timezone(self):
        tz = self.cleaned_data['timezone']
        if tz == None or tz == "":
            tz = 0
        return tz

    def clean_document(self):
        content = self.cleaned_data['document']
        if content._size > settings.COURSE_DOCUMENT_MAX_UPLOAD_SIZE:
            raise forms.ValidationError( ('Please keep filesize under %s. Current filesize %s')
                % (filesizeformat(settings.COURSE_DOCUMENT_MAX_UPLOAD_SIZE), filesizeformat(content._size)))
        _, fileExtension = os.path.splitext(content.name)
        content.name = generateRandomFilename(fileExtension)
        return content

class EditHomeworkRequestForm(forms.Form):
    name = forms.CharField(max_length=200)
    description = forms.CharField(max_length=1000, required=False)
    topic_id = forms.CharField(required=False)
    start = forms.DateTimeField(input_formats=settings.VALID_TIME_INPUTS)
    deadline = forms.DateTimeField(input_formats=settings.VALID_TIME_INPUTS)
    timezone = forms.IntegerField()
    course_id = forms.CharField()
    hw_req_id = forms.CharField()

    def clean(self):
        cleaned_data = super(EditHomeworkRequestForm, self).clean()

        courses = Course.objects.filter(id=cleaned_data.get("course_id"))
        if len(courses) != 1:
            raise forms.ValidationError("Not a valid number of courses with this course_id!")
        cleaned_data['course'] = courses[0]

        hw_reqs = CourseHomeworkRequest.objects.filter(id=cleaned_data.get("hw_req_id"))
        if len(hw_reqs) != 1:
            raise forms.ValidationError("Not a valid number of homework requests with this hw_req_id!")
        cleaned_data['homework_request'] = hw_reqs[0]

        if cleaned_data['homework_request'].course != cleaned_data['course']:
            raise forms.ValidationError("The course you are submitting does have this homework")

        if cleaned_data['topic_id']:
            topics = CourseTopic.objects.filter(id=cleaned_data['topic_id'], course=cleaned_data["course"])
            if topics: 
                cleaned_data["topic"] = topics[0]
            else:
                raise forms.ValidationError("The selected topic does not belong to this course")
        else:
            cleaned_data["topic"] = None
        
        return cleaned_data

    def clean_timezone(self):
        tz = self.cleaned_data['timezone']
        if tz == None or tz == "":
            tz = 0
        return tz

class SubmitHomeworkGradesForm(forms.Form):
    hw_req_id = forms.IntegerField()
    save = forms.BooleanField(required=False)
    publish = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        hw_req_id = args[0].get('hw_req_id')
        super(SubmitHomeworkGradesForm, self).__init__(*args, **kwargs)
        if not hw_req_id:
            return 
        reqs = CourseHomeworkRequest.objects.filter(id=hw_req_id)
        if not reqs:
            return
        hw = reqs[0]
        students = hw.course.students.all()
        for st in students:
            for i in range(1,hw.number_files+1):
                field_name = st.username + "-" + str(i)
                self.fields[field_name] = forms.FloatField(required=False, \
                                        validators=[MinValueValidator(0.0), \
                                                    MaxValueValidator(100.0)])

    def clean(self):
        cleaned_data = super(SubmitHomeworkGradesForm, self).clean()

        homework_requests = CourseHomeworkRequest.objects.filter(id=cleaned_data.get("hw_req_id"))
        if len(homework_requests) != 1:
            raise forms.ValidationError("Not a valid number of homework requests with this homeworkRequest_id!")
        hw_req = homework_requests[0]
        cleaned_data['homework_request'] = hw_req

        return cleaned_data

class VoteReviewForm(forms.Form):
    review_id = forms.CharField()
    vote_type = forms.CharField()

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

class UpdateInfoForm(forms.Form):
    description = forms.CharField(required=False, max_length=5000)
    additional_info = forms.CharField(required=False, max_length=5000)
    abbreviation = forms.CharField(required=False, max_length=50)

class UpdateSyllabusForm(forms.Form):
    entry_name = forms.CharField(max_length=200)
    entry_description = forms.CharField(max_length=500)
    entry_id = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super(UpdateSyllabusForm, self).clean()

        entry_id = cleaned_data.get("entry_id")
        if entry_id:
            entries = CourseTopic.objects.filter(id=entry_id)
            if len(entries) != 1:
                raise forms.ValidationError("Not a valid number of entries with this entry_id!")
            cleaned_data['course_topic'] = entries[0]

        return cleaned_data

class DeleteSyllabusEntryForm(forms.Form):
    entry_id = forms.CharField()

    def clean(self):
        cleaned_data = super(DeleteSyllabusEntryForm, self).clean()

        entries = CourseTopic.objects.filter(id=cleaned_data.get("entry_id"))
        if len(entries) != 1:
            raise forms.ValidationError("Not a valid number of entries with this entry_id!")
        cleaned_data['course_topic'] = entries[0]

        return cleaned_data


class TAPermissionsForm(forms.Form):
    user_id = forms.IntegerField()
    approve_registrations = forms.BooleanField(required=False)
    mail_students = forms.BooleanField(required=False)
    manage_resources = forms.BooleanField(required=False)
    assign_homework = forms.BooleanField(required=False)
    grade_homework = forms.BooleanField(required=False)
    manage_forum = forms.BooleanField(required=False)
    manage_info = forms.BooleanField(required=False)

class NewTAForm(forms.Form):
    user = forms.EmailField()

class RemoveTAForm(forms.Form):
    user_id = forms.IntegerField()