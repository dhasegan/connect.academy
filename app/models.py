from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.conf import settings 
from app.course_info import *






###########################################################################
####################### User Related Models ###############################
###########################################################################


USER_TYPE_STUDENT = 0
USER_TYPE_PROFESSOR = 1
USER_TYPE_ADMIN = 2 # The administator of at least 1 category, who is not a professor

USER_TYPES = (
    (USER_TYPE_STUDENT, "student"),
    (USER_TYPE_PROFESSOR, "professor"),
    (USER_TYPE_ADMIN, "admin")
)

# Inheriting from Base Class 'User'
class jUser(User):

    user_type = models.IntegerField(choices=USER_TYPES, default=USER_TYPE_STUDENT)
    university = models.ForeignKey('University',null = True) 
    
    # For professors only 
    # True if they have been confirmed to be professors)
    is_confirmed = models.NullBooleanField(default = False)
    # Courses the user is enrolled to
    courses_enrolled = models.ManyToManyField('Course', related_name='students', 
                                               through = 'StudentCourseRegistration')

    # courses the user is managing (i.e: if they're professors)
    courses_managed = models.ManyToManyField('Course', related_name='professors',
                                              through = 'ProfessorCourseRegistration')

    # may turn out useful - this might also need approval,
    # so we may have to create another table to handle the ManyToMany relation
    majors = models.ManyToManyField('Major', related_name = 'students')

    # !! 
    # Relations declared in other models define the following:
    #    categories_managed: (<juser>.categories_managed.all() returns all categories that have <juser> 
    #    as an admin)
    #    upvoted: (<juser>.upvoted.all() returns all comments that <juser> upvoted)
    #    downvoted: (<juser>.upvoted.all() returns all comments that <juser> downvoted)

    def __unicode__(self):
        return str(self.username)

class StudentCourseRegistration(models.Model):
    student = models.ForeignKey('jUser')
    course = models.ForeignKey('Course')
    is_approved = models.BooleanField(default = False) # True if registration is approved

    def __unicode__(self):
        return "Register" + str(self.student)

class ProfessorCourseRegistration(models.Model):
    professor = models.ForeignKey('jUser')
    course = models.ForeignKey('Course')
    is_approved = models.BooleanField(default = False) # True if registration is approved

    def __unicode__(self):
        return "Register" + str(self.professor)









###########################################################################
################# University/Course Related Models ########################
###########################################################################

COURSE_TYPE_UG = 0
COURSE_TYPE_GRAD = 1
COURSE_TYPES = (
    (COURSE_TYPE_UG,"Undergraduate"),
    (COURSE_TYPE_GRAD, "Graduate")
)

class Major(models.Model):
    # We could use this later to add more functionality, 
    # we can add major requirements, courses etc.
    name = models.CharField(max_length = 200)
    abbreviation = models.CharField(max_length=10, blank = True, null=True)
    # !!
    # Relations declared in other models define the following:
    #    courses: (<major>.courses.all() returns all courses of <major>) 
    #    students: (<major>.students.all() returns all students of <major>)

    def __unicode__(self):
        return str(self.name)

class Course(models.Model):
    course_id = models.IntegerField()
    name = models.CharField(max_length=200)
    course_type = models.IntegerField(choices=COURSE_TYPES, default = COURSE_TYPE_UG)
    credits = models.FloatField()
    description = models.CharField(max_length=5000, blank=True, null = True)
    additional_info = models.CharField(max_length=5000, blank=True, null=True)
    abbreviation = models.CharField(max_length=50, blank=True, null=True)
    slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to='courses')
    university = models.ForeignKey('University', related_name = 'courses')
    category = models.ForeignKey('Category', related_name = 'courses')
    tags = models.ManyToManyField('Tag',related_name='courses')
    majors = models.ManyToManyField('Major', related_name='courses')
    prerequisites = models.ManyToManyField('self',related_name='next_courses')
    # !!
    # Relations declared in other models define the following:
    #   instructors (<course>.instructors.all() returns all instructors of <course>)
    #   students    (<course>.students.all()    returns all students    of <course>)
    #   next_courses (<course>.next_courses.all() returns all courses that have
    #   <course> as a prerequisite)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Course, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.name)



class Tag(models.Model):
    # Besides name, we might need to add more fancy things to tags (we can group them etc)
    name = models.CharField(max_length = 100)
    # !!
    # Relations declared in other models define the following:
    #   courses (<tag>.courses.all() returns all courses of that have <tag>)

    def __unicode__(self):
        return str(self.name)



class University(models.Model):
    name = models.CharField(max_length=150)
    # Relations declared in other models define the following:
    #   domains (<university>.domains.all() returns all domains of a university)
    #   courses (<university>.courses.all() returns all courses of a university)

    def __unicode__(self):
        return str(self.name)



class Category(models.Model):
    parent = models.ForeignKey('self',null = True) # Parent category
    level = models.IntegerField(null=True) # The level in which the category is positioned in the tree
    name = models.CharField(max_length = 150)
    abbreviation = models.CharField(max_length = 10)
    admins = models.ManyToManyField('jUser', related_name = 'categories_managed')
    # !!
    # Relations declared in other models define the following:
    #   courses (<category>.courses.all() returns all courses that are direct children of <category>)
    
    def getAdmins(self):
        # Gets the "closest" administrators of a category. 
        admins = self.admins.all()
        if len(admins) > 0:
            return admins
        elif self.parent != None: # if not root
            return self.parent.getAdmins()
        else:
            return None

    def getAllAdmins(self):
        # get all people with administrator rights of this category
        # (i.e: including admins of parent categories)
        admins = self.admins.all()
        if self.parent != None:
            admins += self.parent.getAllAdmins()
        return admins


    def getAllCourses(self):
        # Gets all the courses that are descendants of this category
        allcourses = self.courses.all()
        children = Category.objects.filter(parent__id = self.id)
        for child in children:
            allcourses += child.getAllCourses()

        return allcourses

    def __unicode__(self):
        return str(self.name)

class Domain(models.Model):
    # University Domain
    name = models.CharField(max_length=200,unique = True)
    university = models.ForeignKey('University', related_name='domains')

    def __unicode__(self):
        return str(self.name)


class WikiPage(models.Model):
    name = models.CharField(max_length=50,primary_key=True)
    content = models.TextField(blank=True)

    def __unicode__(self):
        return str(self.name)








###########################################################################
####################### Posts, Ratings, Comments ##########################
###########################################################################

RATING_MIN = 1
RATING_MAX = 5
OVERALL_R = 'ALL'
WORKLOAD_R = 'WKL'
DIFFICULTY_R = 'DIF'
PROFESSOR_R = 'PRF'
RATING_TYPES = (
    (OVERALL_R, 'Overall'),
    (WORKLOAD_R, 'Workload'),
    (DIFFICULTY_R, 'Difficulty'),
    (PROFESSOR_R, 'Professor')
)


class Rating(models.Model):
    user = models.ForeignKey('jUser', related_name='rated')
    course = models.ForeignKey('Course')
    rating = models.FloatField()
    rating_type = models.CharField( max_length=3,
                                    choices=RATING_TYPES,
                                    default=OVERALL_R)
    professor = models.ForeignKey('jUser', related_name='been_rated', null=True, blank=True)

    def __unicode__(self):
        return str(self.rating)

class Comment(models.Model):
    course = models.ForeignKey('Course')
    comment = models.CharField(max_length=5000)
    datetime = models.DateTimeField(auto_now=True)

    posted_by = models.ForeignKey('jUser', null=True)
    upvoted_by = models.ManyToManyField('jUser', related_name='upvoted')
    downvoted_by = models.ManyToManyField('jUser', related_name='downvoted')

    def __unicode__(self):
        return str(self.comment)

###########################################################################
####################### Questions, Answers ################################
###########################################################################
