from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.conf import settings 
from app.course_info import *

USER_TYPE_STUDENT = 0
USER_TYPE_INSTRUCTOR = 1
USER_TYPE_DEPARTMENT_ADMIN = 2
USER_TYPE_UNIVERSITY_ADMIN = 3
# USER_TYPE_ADMIN = 4 (for our accounts, when we build an interface for our admins.)
USER_TYPES = (
    (USER_TYPE_STUDENT, "student"),
    (USER_TYPE_INSTRUCTOR, "instructor"),
    (USER_TYPE_DEPARTMENT_ADMIN, "department_admin"),
    (USER_TYPE_UNIVERSITY_ADMIN, "university_admin"),
    #(USER_TYPE_ADMIN, "global_admin")
)

class jUser(User):

    user_type = models.IntegerField(choices=USER_TYPES,default=USER_TYPE_STUDENT)
    departments = models.ManyToManyField('Department', null=True ,blank=True)
    university = models.ForeignKey('University',default = 1)
    is_confirmed = models.NullBooleanField(default = False)  # For instructors only 
                                                             # True if they have been confirmed to be instructors)
    courses = models.ManyToManyField('Course')
    

    class Meta:
        # Permissions associated with users - besides add/change/delete user
        permissions = (
            ("crud_students", "Can perform CRUD operations on students"),
            ("crud_instructors", "Can perform CRUD operations on instructors"),
            ("crud_department_admins", "Can perform CRUD operations on students"),
            ("add_university_admins", "Can add new university admins"),
            ("delete_university_admins", "Can delete university admins"),
            ("change_university_admins", "Can change university admins"),
            ("approve_course_student", "Can approve a student's course registration"),
            ("approve_course_instructor", "Can approve an instructor's request to teach a course")
        )    

class InstructorCourseRegistration:
    instructor = models.ForeignKey('jUser')
    course = models.ForeignKey('Course')

class StudentCourseRegistration:
    student = models.ForeignKey('jUser')
    course = models.ForeignKey('Course')


class Professor(models.Model):
    name = models.CharField(max_length=50)
    department = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return str(self.name)

RATING_MIN = 1
RATING_MAX = 5

class Rating(models.Model):
    user = models.ForeignKey('jUser')
    course = models.ForeignKey('Course')
    rating = models.FloatField()
    rating_type = models.CharField( max_length=3,
                                    choices=RATING_TYPES,
                                    default=OVERALL_R)

    def __unicode__(self):
        return str(self.rating)

class Professor_Rating(Rating):
    prof = models.ForeignKey('Professor')

    def __unicode__(self):
        return "Rating " + str(self.prof.name)

class Course(models.Model):
    course_id = models.CharField( max_length=10 )
    course_type = models.CharField( max_length=3,
                                    choices=COURSE_TYPES,
                                    default=LECTURE)
    name = models.CharField(max_length=200)
    instructors = models.ManyToManyField('Professor')
    credits = models.FloatField()
    description = models.CharField(max_length=5000, blank=True, null=True)
    additional_info = models.CharField(max_length=5000, blank=True, null=True)
    sections_info = models.CharField(max_length=5000, blank=True, null=True)
    catalogue = models.CharField(max_length=300) # Create separate divisions
    grades = models.CharField(max_length=1000, blank=True, null=True)
    grades_info = models.CharField(max_length=5000, blank=True, null=True)
    abbreviation = models.CharField(max_length=50, blank=True, null=True)
    participants = models.CharField(max_length=10, blank=True, null=True)
    hours_per_week = models.CharField(max_length=10, blank=True,null=True)

    slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to='courses')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Course, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.name)

class Comment(models.Model):
    course = models.ForeignKey('Course')
    comment = models.CharField(max_length=1000)
    datetime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "Comm" + str(self.id)

class University(models.Model):
    name = models.CharField(max_length=150)
    domains = models.ManyToManyField('Domain')
    departments = models.ManyToManyField('Department')

class Domain(models.Model):
    name = models.CharField(max_length=200,unique = True)

class Department(models.Model):
    name = models.CharField(max_length=200)

class WikiPage(models.Model):
    name = models.CharField(max_length=50,primary_key=True)
    content = models.TextField(blank=True)

    def __unicode__(self):
        return str(self.name)