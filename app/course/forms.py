import hashlib
import random
import os

from django import forms
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
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
        try:
            course = Course.objects.get(id=cleaned_data.get("course_id"))
        except ObjectDoesNotExist, MultipleObjectsReturned:
            raise forms.ValidationError("This course does not exist")

        cleaned_data['course'] = course

        if rtype == PROFESSOR_R:
            if not 'profname' in cleaned_data:
                raise forms.ValidationError("There is no professor name for the form!")

            try:
                prof = jUser.objects.get(username=cleaned_data['profname'])
            except ObjectDoesNotExist, MultipleObjectsReturned:
                raise forms.ValidationError("A professor with this username does not exist")
            cleaned_data['prof'] = prof

        return cleaned_data


class SubmitCommentForm(forms.Form):
    course_id = forms.CharField()
    comment = forms.CharField(max_length=5000)
    anonymous = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super(SubmitCommentForm, self).clean()

        try:
            course = Course.objects.filter(id=cleaned_data.get("course_id"))
        except ObjectDoesNotExist, MultipleObjectsReturned:
            raise forms.ValidationError("This course does not exist")
        cleaned_data['course'] = course

        return cleaned_data

class SubmitDocumentForm(forms.Form):
    name = forms.CharField(max_length=200)
    document = forms.FileField()
    topic_id = forms.CharField(required=False)
    module_id = forms.CharField(required = False)
    description = forms.CharField(max_length=1000, required=False)
    course_id = forms.CharField()
    url = forms.CharField()
    access_level = forms.IntegerField()

    def clean(self):
        cleaned_data = super(SubmitDocumentForm, self).clean()

        try:
            course = Course.objects.get(id=cleaned_data.get("course_id"))
        except ObjectDoesNotExist, MultipleObjectsReturned:
            raise forms.ValidationError("This course does not exist")
        cleaned_data['course'] = course

        if cleaned_data['topic_id']:
            try:
                topic = CourseTopic.objects.get(id=cleaned_data['topic_id'], course=cleaned_data["course"])
            except ObjectDoesNotExist, MultipleObjectsReturned:
                raise forms.ValidationError("The selected topic does not belong to this course")
            cleaned_data["topic"] = topic
        else:
            cleaned_data["topic"] = None

        if cleaned_data['module_id']:
            try:
                cleaned_data['module'] = CourseModule.objects.get(id=cleaned_data['module_id'], course=cleaned_data["course"])
            except ObjectDoesNotExist, MultipleObjectsReturned: 
                raise forms.ValidationError("The selected module does not exist or it does not belong to this course")
        else:
            cleaned_data['module'] = None


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
        
        try:
            doc = CourseDocument.objects.get(id=cleaned_data.get("doc_id"))
        except ObjectDoesNotExist, MultipleObjectsReturned:
            raise forms.ValidationError("Not a valid number of documents with this doc_id!")
        
        cleaned_data['doc_obj'] = doc

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
        try:
            course = Course.objects.get(id=cleaned_data.get("course_id"))
        except ObjectDoesNotExist, MultipleObjectsReturned:
            raise forms.ValidationError("Not a valid number of courses with this course_id!")
        cleaned_data['course'] = course
        try:
            hw_req = CourseHomeworkRequest.objects.get(id=cleaned_data.get("homework_request_id"))
        except ObjectDoesNotExist, MultipleObjectsReturned:
            raise forms.ValidationError("Not a valid number of homework requests with this homeworkRequest_id!")
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

        if not hw_req.course == course:
            raise forms.ValidationError("Integration error!")

        return cleaned_data

class SubmitHomeworkRequestForm(forms.Form):
    name = forms.CharField(max_length=200)
    description = forms.CharField(max_length=1000, required=False)
    topic_id = forms.CharField(required=False)
    start = forms.DateTimeField(input_formats=settings.VALID_TIME_INPUTS)
    deadline = forms.DateTimeField(input_formats=settings.VALID_TIME_INPUTS)
    timezone = forms.IntegerField()
    module_id = forms.CharField(required=False)
    nr_files = forms.IntegerField(validators=[MinValueValidator(HOMEWORK_MIN_FILES),
                                              MaxValueValidator(HOMEWORK_MAX_FILES)])
    document = forms.FileField(required=False)
    
    course_id = forms.CharField()

    def clean(self):
        cleaned_data = super(SubmitHomeworkRequestForm, self).clean()
        try:
            course = Course.objects.get(id=cleaned_data.get("course_id"))
        except ObjectDoesNotExist, MultipleObjectsReturned:
            raise forms.ValidationError("Not a valid number of courses with this course_id!")
        cleaned_data['course'] = course

        if cleaned_data['topic_id']:
            try:
                cleaned_data['topic'] = CourseTopic.objects.get(id=cleaned_data['topic_id'], course=cleaned_data["course"])
            except ObjectDoesNotExist, MultipleObjectsReturned: 
                raise forms.ValidationError("The selected topic does not exist or it does not belong to this course")      
        else:
            cleaned_data["topic"] = None

        if cleaned_data['module_id']:
            try:
                cleaned_data['module'] = CourseModule.objects.get(id=cleaned_data['module_id'], course=cleaned_data["course"])
            except ObjectDoesNotExist, MultipleObjectsReturned: 
                raise forms.ValidationError("The selected module does not exist or it does not belong to this course")
        else:
            cleaned_data["module"] = None

        return cleaned_data

    def clean_timezone(self):
        tz = self.cleaned_data['timezone']
        if tz == None or tz == "":
            tz = 0
        return tz

    def clean_document(self):
        content = self.cleaned_data['document']
        if not content:
            return content
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
    module_id = forms.CharField(required=False)
    start = forms.DateTimeField(input_formats=settings.VALID_TIME_INPUTS)
    deadline = forms.DateTimeField(input_formats=settings.VALID_TIME_INPUTS)
    timezone = forms.IntegerField()
    course_id = forms.CharField()
    hw_req_id = forms.CharField()

    def clean(self):
        cleaned_data = super(EditHomeworkRequestForm, self).clean()
        try:
            course = Course.objects.get(id=cleaned_data.get("course_id"))
        except ObjectDoesNotExist, MultipleObjectsReturned:
            raise forms.ValidationError("Not a valid number of courses with this course_id!")

        cleaned_data['course'] = course

        try:
            hw_req = CourseHomeworkRequest.objects.get(id=cleaned_data.get("hw_req_id"))
        except ObjectDoesNotExist, MultipleObjectsReturned:
            raise forms.ValidationError("Not a valid number of homework requests with this hw_req_id!")
        cleaned_data['homework_request'] = hw_req

        if cleaned_data['homework_request'].course_id != cleaned_data['course'].id:
            raise forms.ValidationError("The course you are submitting does have this homework")

        if cleaned_data['topic_id']:
            try:
                topic = CourseTopic.objects.get(id=cleaned_data['topic_id'], course=cleaned_data["course"])
            except ObjectDoesNotExist, MultipleObjectsReturned: 
                raise forms.ValidationError("The selected topic does not belong to this course")
            
            cleaned_data["topic"] = topic
                
        else:
            cleaned_data["topic"] = None

        if cleaned_data['module_id']:
            try:
                cleaned_data['module'] = CourseModule.objects.get(id=cleaned_data['module_id'], course=cleaned_data["course"])
            except ObjectDoesNotExist, MultipleObjectsReturned: 
                raise forms.ValidationError("The selected module does not exist or it does not belong to this course")
        else:
            cleaned_data['module'] = None
        
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
        try:
            hw = CourseHomeworkRequest.objects.filter(id=hw_req_id)
        except ObjectDoesNotExist, MultipleObjectsReturned:
            return
    
        students = hw.course.students.all()
        for st in students:
            for i in range(1,hw.number_files+1):
                field_name = st.username + "-" + str(i)
                self.fields[field_name] = forms.FloatField(required=False, \
                                        validators=[MinValueValidator(0.0), \
                                                    MaxValueValidator(100.0)])

    def clean(self):
        cleaned_data = super(SubmitHomeworkGradesForm, self).clean()
        try:
            hw_req = CourseHomeworkRequest.objects.get(id=cleaned_data.get("hw_req_id"))
        except ObjectDoesNotExist, MultipleObjectsReturned:
            raise forms.ValidationError("Not a valid number of homework requests with this homeworkRequest_id!")
        cleaned_data['homework_request'] = hw_req

        return cleaned_data

class VoteReviewForm(forms.Form):
    review_id = forms.CharField()
    vote_type = forms.CharField()

    def clean(self):
        cleaned_data = super(VoteReviewForm, self).clean()
        try:
            review = Review.objects.get(id=cleaned_data.get("review_id"))
        except ObjectDoesNotExist, MultipleObjectsReturned:
            raise forms.ValidationError("Not a valid number of reviews with this review_id!")
        cleaned_data['review'] = review

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
            try:
                entry = CourseTopic.objects.get(id=entry_id)
            except ObjectDoesNotExist, MultipleObjectsReturned:
                raise forms.ValidationError("Not a valid number of entries with this entry_id!")
            cleaned_data['course_topic'] = entry

        return cleaned_data


class DeleteSyllabusEntryForm(forms.Form):
    entry_id = forms.CharField()

    def clean(self):
        cleaned_data = super(DeleteSyllabusEntryForm, self).clean()
        try:
            entry = CourseTopic.objects.get(id=cleaned_data.get("entry_id"))
        except ObjectDoesNotExist, MultipleObjectsReturned:
            raise forms.ValidationError("Not a valid number of entries with this entry_id!")
        cleaned_data['course_topic'] = entry

        return cleaned_data

class NewCourseModuleForm(forms.Form):
    module_name = forms.CharField(max_length=200)

class UpdateCourseModuleForm(forms.Form):
    module_name = forms.CharField(max_length=200)
    module_id = forms.CharField()

    def clean(self):
        cleaned_data = super(UpdateCourseModuleForm, self).clean()
        try:
            module = CourseModule.objects.get(id=cleaned_data.get("module_id"))
        except ObjectDoesNotExist, MultipleObjectsReturned:
            raise forms.ValidationError("Not a valid number of course modules with this module_id")
        cleaned_data['course_module'] = module

        return cleaned_data

class DeleteCourseModuleForm(forms.Form):
    module_id = forms.CharField()

    def clean(self):
        cleaned_data = super(DeleteCourseModuleForm, self).clean()
        try:
            module = CourseModule.objects.get(id=cleaned_data.get("module_id"))
        except ObjectDoesNotExist, MultipleObjectsReturned:
            raise forms.ValidationError("Not a valid number of course modules with this module_id")
        cleaned_data['course_module'] = module

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