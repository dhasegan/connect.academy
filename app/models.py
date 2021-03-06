from datetime import * #datetime
import pytz # timezones
from django.utils import timezone
import versioning
import re 
from guardian.shortcuts import assign_perm

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.conf import settings 
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django import forms
from django.contrib import messages
from app.helpers import get_slug_for



###########################################################################
####################### User Related Models ###############################
###########################################################################


USER_TYPE_STUDENT = 0
USER_TYPE_PROFESSOR = 1
USER_TYPE_ADMIN = 2 # The administator of at least 1 category, who is not a professor
USER_TYPE_ALUMNUS = 3 
USER_TYPES = (
    (USER_TYPE_STUDENT, "student"),
    (USER_TYPE_PROFESSOR, "professor"),
    (USER_TYPE_ADMIN, "admin"),
    (USER_TYPE_ALUMNUS, "alumnus"),
)

def determine_profilepic_filename(instance, filename):
        parts = filename.split('.')
        if len(parts) > 1:
            extension = parts[-1]
        else:
            extension = "jpg"
        return "users/%s/%s" % (instance.username, "profile_picture." + extension)
        

# Inheriting from Base Class 'User'
class jUser(User):

    user_type = models.IntegerField(choices=USER_TYPES, default=USER_TYPE_STUDENT)
    university = models.ForeignKey('University',null = True) 
    
    summary = models.CharField(max_length=500, null=True) 
    profile_picture = models.ImageField(upload_to=determine_profilepic_filename, null=True)
    # For professors only 
    # True if they have been confirmed to be professors)
    is_confirmed = models.NullBooleanField(default = False)

    # True if it's a fake account (one that we created before user login/registration (e.g: some professors))
    is_fake = models.NullBooleanField(default = False)
    # Courses the user is enrolled to
    courses_enrolled = models.ManyToManyField('Course', related_name='students', 
                                               through = 'StudentCourseRegistration')
    course_modules = models.ManyToManyField('CourseModule', related_name='students',
                                               through='StudentCourseRegistration')
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
    #    downvoted: (<juser>.downvoted.all() returns all comments that <juser> downvoted)
    #    appointments(<jUser>.appointments.all() returns all the appointments of that <jUser>)

    #    contributed_to: (<juser>.contributed_to.all()) returns all the wikis the user has contributed to)
    #    posts_following: (<juser>.posts_following.all() returns all forum posts that <juser> is following)

    
    def is_student(self):
        return self.user_type == USER_TYPE_STUDENT

    def is_professor(self):
        return self.user_type == USER_TYPE_PROFESSOR

    def is_admin(self):
        return self.user_type == USER_TYPE_ADMIN

    def is_alumnus(self):
        return self.user_type == USER_TYPE_ALUMNUS

    def is_student_of(self, course):
        if not self.is_student():
            return False
        is_registered = StudentCourseRegistration.objects.filter(student=self, course=course, is_approved = True).exists()
        return self.is_student() and is_registered

    def is_professor_of(self, course):
        is_registered = ProfessorCourseRegistration.objects.filter(professor=self, course=course, is_approved = True).exists()
        return self.is_professor() and is_registered

    def is_assistant_of(self,course):
        return course.teaching_assistants.filter(id=self.id).exists()

    def is_admin_of(self, course):
        if not self.is_admin():
            return False
        categories = self.categories_managed.all()
        for category in categories:
            if course in category.get_all_courses():
                return True
        return False

    def is_following(self,post):
        forum_type = post.forum.forum_type
        if forum_type == FORUM_COURSE:
            course = post.forum.forumcourse.course
            return self.is_student_of(course) or self.is_professor_of(course) or self.posts_following.filter(id=post.id).exists()
        else:
            return self.posts_following.filter(id=post.id).exists()

    def get_courses(self):
        return self.courses_enrolled.all() | self.courses_assisted.all() | self.courses_managed.all()


    def is_participant_of(self,course):
        return self.get_courses().values('id').filter(id=course.id).exists()

    def __unicode__(self):
        return str(self.username)


class StudentCourseRegistration(models.Model):
    student = models.ForeignKey('jUser')
    course = models.ForeignKey('Course')
    module = models.ForeignKey('CourseModule',related_name='student_registrations', null=True)
    is_approved = models.BooleanField(default = False) # True if registration is approved
    reg_time = models.DateField(default = timezone.now())
    

    def __unicode__(self):
        return str(self.student)



class ProfessorCourseRegistration(models.Model):
    professor = models.ForeignKey('jUser')
    course = models.ForeignKey('Course')
    is_approved = models.BooleanField(default = False) # True if registration is approved
    reg_time = models.DateField(default=timezone.now())

    def __unicode__(self):
        return str(self.professor)

    def save(self, *args, **kwargs):
        super(ProfessorCourseRegistration, self).save(*args, **kwargs)
        if self.is_approved:
            for perm in Course._meta.permissions:
                if not self.professor.has_perm(perm[0], self.course):
                    assign_perm(perm[0], self.professor, self.course) # perm[0] is the name of the permission











###########################################################################
################# University/Course Related Models ########################
###########################################################################

# Course types
COURSE_TYPE_UG = 0
COURSE_TYPE_GRAD = 1
COURSE_TYPES = (
    (COURSE_TYPE_UG,"Undergraduate"),
    (COURSE_TYPE_GRAD, "Graduate")
)

# Registration statuses
COURSE_REGISTRATION_OPEN = 0 # The user can register for this course
COURSE_REGISTRATION_PENDING = 1 # Registration for this course is pending approval
COURSE_REGISTRATION_REGISTERED = 2 # User is registered for this course
COURSE_REGISTRATION_NOT_ALLOWED = 3 # User is not allowed to register for this course

REGISTRATION_STATUSES = (
    (COURSE_REGISTRATION_OPEN, "Open"),
    (COURSE_REGISTRATION_PENDING, "Pending"),
    (COURSE_REGISTRATION_REGISTERED, "Registered"),
    (COURSE_REGISTRATION_NOT_ALLOWED, "Not_Allowed")
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

AVAILABLE_COURSE_PAGES = ['activity', 'info', 'connect', 'wiki', 'resources', 'teacher']
AVAILABLE_COURSE_TEACHER_PAGES = ['registered', 'pending', 'upload', 'homework', 'forum', 'details', 'assistants']

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
    university = models.ForeignKey('University', related_name='courses')
    category = models.ForeignKey('Category', null=True, default=None, related_name='courses')
    tags = models.ManyToManyField('Tag', related_name='courses')
    majors = models.ManyToManyField('Major', related_name='courses')
    prerequisites = models.ManyToManyField('self', related_name='next_courses')
    external_link = models.CharField(max_length=200, null=True, blank=True)
    teaching_assistants = models.ManyToManyField('jUser', related_name='courses_assisted')
    # !!
    # Relations declared in other models define the following:
    #   forum (<course>.forum returns the forum of the <course>)
    #   professors (<course>.professor.all() returns all professors of <course>)
    #   students    (<course>.students.all()    returns all students    of <course>)
    #   next_courses (<course>.next_courses.all() returns all courses that have
    #                 <course> as a prerequisite)
    #   course_topics (<course>.course_topics.all() returns all topics of the <course>)
    #   appointments (<course>.appointments.all() returns all the appointment of the <course>)
    #   activities (<course>.activities.all() returns all (newsfeed) activities of <course>)
    #   modules (<course>.modules.all() returns all course modules of <course>)
    class Meta:
        permissions = (
            ('approve_registrations', "Approve students' registrations."),
            ('mail_students', "See and e-mail all students."),
            ('manage_resources', "Manage course resources (Upload documents)"),
            ('assign_homework', "Assign Homework"),
            ('grade_homework', "Grade homework"),
            ('manage_forum', "Manage the course forum and see forum stats"),
            ('manage_info', "Manage course info (description, syllabus etc...)"),
        )

    def get_non_topic_documents(self):
        return self.documents.filter(course_topic=None)

    # gets the registration status of this course for the given user
    # Registration status is one of the following:
    #   COURSE_REGISTRATION_OPEN       (0): The student can register for the course
    #   COURSE_REGISTRATION_PENDING     (1): Registration is pending approval
    #   COURSE_REGISTRATION_REGISTERED    (2): User is registered for the course
    #   COURSE_REGISTRATION_NOT_ALLOWED     (3): User is not allowed to register for the course

    def get_registration_status(self,user):
        registration = None
        if user.user_type == USER_TYPE_STUDENT:
            try:
                registration = StudentCourseRegistration.objects.get(student=user, course = self)
            except Exception:
                pass
        elif user.user_type == USER_TYPE_PROFESSOR:
            try:
                registration = ProfessorCourseRegistration.objects.get(professor = user, course = self)
            except Exception:
                pass
        else:
            return COURSE_REGISTRATION_NOT_ALLOWED # Not a user, not a professor

        if registration is None:
            if user.university == self.university and user.is_active:
                return COURSE_REGISTRATION_OPEN
            else:
                return COURSE_REGISTRATION_NOT_ALLOWED
        else:
            if registration.is_approved:
                return COURSE_REGISTRATION_REGISTERED
            else:
                return COURSE_REGISTRATION_PENDING

        return None # This line will never be reached

        

    def get_registration_deadline(self):
        category = self.category
        if category is not None:
            return category.get_registration_deadline()
        else:
            return None

    def get_rating(self, rating_type):
        ratings = self.rating_set.filter(rating_type=rating_type)
        if not ratings:
            return None
        return sum([cur.rating for cur in ratings]) / len(ratings)

    def get_catalogue(self):
        course_path = None
        university_category = self.university.get_university_category()
        category = self.category
        while category is not None and category != university_category:
            course_path = "%s > %s" % (category.name, course_path) if course_path else category.name
            category = category.parent
        return course_path

    def can_edit_wiki(self, user):
        return user.university.id == self.university.id

    def save(self, *args, **kwargs):
        self.slug = get_slug_for(Course, self.pk, self.name)
        super(Course, self).save(*args, **kwargs)
        ForumCourse.objects.get_or_create(course=self)


   
    def __unicode__(self):
        return str(self.name)


# Model that represents a course topic. Many topics of the same course form the 
# course's syllabus 
class CourseTopic(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    course = models.ForeignKey("Course", related_name="course_topics");

    # Relations declared in other models define the following:
    #    forums (<course_topic>.forums.all() returns all forums of  <course_topic>)
    #    homework_requests (<course_topic>.homework_requests.all() returns all homework requests of <course_topic>)

    class Meta:
        order_with_respect_to = 'course'
        # Documentation of this field
        # https://docs.djangoproject.com/en/dev/ref/models/options/#order-with-respect-to
        # It basically allows us to change the order of the topics of the same course.
        # <course>.get_topic_order() returns the primary keys (ids) of the topics of
        # <course> in the current order
        # To set the order, call <course>.set_topic_order(ls) where ls is the ordered
        # list of the primary keys (ids) of the topics.

    def save(self, *args, **kwargs):
        tags = ForumTopicTag.objects.filter(topic=self)
        super(CourseTopic, self).save(*args, **kwargs)
        if not len(tags):
            tag_name = ForumTag.create_tag_name(self.name)
            forum = ForumCourse.objects.get(course=self.course).forum_ptr
            ForumTopicTag.objects.create(name=tag_name, tag_type=FORUMTAG_TOPIC, \
                forum=forum, topic=self)
        else:
            tag = tags[0]
            tag.name = ForumTag.create_tag_name(self.name)
            tag.save()

    def __unicode__(self):
        return str(self.name)



class CourseModule(models.Model):
    name = models.CharField(max_length=200)
    course = models.ForeignKey('Course',related_name='modules')
    # !!
    # Relations declared in other models define the following:
    #   homework_requests
    #   student_registrations
    #   activities
    #   documents
    #   appointments


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
    #   domains (<university>.domains.all() returns all domains of <university>)
    #   courses (<university>.courses.all() returns all courses of <university>)
    #   categories (<university>.categories.all() returns all categories of <university>)
    def get_university_category(self):
        connect = Category.objects.get(parent=None)
        univs = self.categories.filter(parent=connect)
        if not univs:
            return None
        return univs[0]

    def __unicode__(self):
        return str(self.name)



class Category(models.Model):
    parent = models.ForeignKey('self',null = True, related_name = 'children') # Parent category
    level = models.IntegerField(null=True) # The level in which the category is positioned in the tree
    university = models.ForeignKey('University', null=True, related_name='categories')
    name = models.CharField(max_length = 150)
    abbreviation = models.CharField(max_length = 10)
    admins = models.ManyToManyField('jUser', related_name = 'categories_managed')

    # Registration deadline
    registration_deadline = models.ForeignKey('CourseRegistrationDeadline', related_name = 'category',null=True)

    # !!
    # Relations declared in other models define the following:
    #   courses (<category>.courses.all() returns all courses that are direct children of <category>)
    #   children (<category>.children.all() returns all child categories of <category>)    


    # get_admins(): Gets the "closest" administrators of a category. 
    def get_admins(self):
        admins = self.admins.all()
        if len(admins) > 0:
            return admins
        elif self.parent != None: # if not root
            return self.parent.get_admins()
        else:
            return None

    # get_all_admins(): Get all people with administrator rights of this category
    # (i.e: including admins of parent categories)
    def get_all_admins(self):
        admins = list(self.admins.all())
        if self.parent != None:
            admins += self.parent.get_all_admins()
        return admins


    # get_all_courses(): Gets all the courses that are descendants of this category
    def get_all_courses(self):
        allcourses = list(self.courses.all())
        children = Category.objects.filter(parent__id = self.id)
        for child in children:
            allcourses += list(child.get_all_courses())

        return allcourses

    # get_registration_deadline (): Finds the course registration deadline for this category
    # (by climbing up to the root of the tree until a category with a deadline is found)
    def get_registration_deadline(self):
        if self.registration_deadline is not None:
            return self.registration_deadline
        elif self.parent is not None:
            return self.parent.get_registration_deadline()
        else:
            return None

    # get_subtree(): Gets the subtree that has this category in the root. The tree is returned as a dictionary,
    # such that when converted to JSON, it follows the specifications to build a Spacetree with 
    # Infoviz (the javascript visualization tool)
    def get_subtree(self):
        tree = {
            'id' : "category-" + str(self.id),
            'name' : self.name,
            'data' : {
                'type': 'category', # category or course
                'admins': [],
            },
            'children' : []
        }
        registration_deadline = self.get_registration_deadline()
        if registration_deadline is not None and registration_deadline.is_open():
            deadline = timezone.localtime(registration_deadline.end)
            time_to_display = datetime.strftime(deadline, "%d/%m/%Y %H:%M (%Z)")
            tree['data']['registration_deadline'] = "Open until " + time_to_display
        else:
            tree['data']['registration_deadline'] = "Closed"

        admins = self.get_all_admins()
        if admins is not None:
            for admin in admins:
                tree['data']['admins'].append({
                    'first_name': admin.first_name,
                    'last_name': admin.last_name,
                    'username': admin.username,
                    'id': admin.id,
                    'own_admin': admin in self.admins.all()

                })


        children = self.children.all()
        courses = self.courses.all()

        for child in children:
            subtree = child.get_subtree()
            tree['children'].append(subtree)

        for course in courses: 
            course_dict = {
                'id': "course-" + str(course.id),
                'name' : course.name,
                'data' : {
                    'type' : 'course',
                    'professors': []
                },
                'children' : []
            }
            for prof in course.professors.all():
                course_dict['data']['professors'].append({
                    'first_name': prof.first_name,
                    'last_name': prof.last_name,
                    'username': prof.username,
                    'id': prof.id
                })
                tree['children'].append(course_dict)

        return tree

    # get_descendants(): Returns all categories that are descendats of this one together with this category
    # this is useful to list the categories in the admin page
    def get_descendants(self):
        descendants = list(self.children.all())
        for cat in descendants:
            descendants2 = list(cat.get_descendants())
            for desc in descendants2:
                if not desc in descendants:
                    descendants.append(desc)
        return descendants

    def __unicode__(self):
        return str(self.name)


DOMAIN_TYPE_STANDARD = 1
DOMAIN_TYPE_ALUMNI = 2
DOMAIN_TYPES = (
    (DOMAIN_TYPE_STANDARD, "standard"),
    (DOMAIN_TYPE_ALUMNI, "alumni"),
)

class Domain(models.Model):
    # University Domain
    name = models.CharField(max_length=200,unique = True)
    university = models.ForeignKey('University', related_name='domains')
    domain_type = models.IntegerField(choices=DOMAIN_TYPES, default=DOMAIN_TYPE_STANDARD)
    def __unicode__(self):
        return str(self.name)

class Deadline(models.Model):
    start = models.DateTimeField(default=timezone.now())
    end = models.DateTimeField()

class CourseRegistrationDeadline(Deadline):
    def is_open(self):
        now = timezone.now()  #using utc as reference time zone
        if now >= self.start and now < self.end:
            return True
        else:
            return False
    # !!
    # Relations declared in other models define the following:
    # category: <courseregistrationdeadline>.category is the category this registration deadline is for




###########################################################################
####################### Reviews, Ratings, Documents, Homework #############
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

class Review(models.Model):
    course = models.ForeignKey('Course')
    review = models.CharField(max_length=5000)
    datetime = models.DateTimeField()

    posted_by = models.ForeignKey('jUser', related_name='reviews_posted')
    anonymous = models.BooleanField(default=False)

    upvoted_by = models.ManyToManyField('jUser', related_name='review_upvoted')
    downvoted_by = models.ManyToManyField('jUser', related_name='review_downvoted')

    def save(self, *args, **kwargs):
        just_created = False
        if not self.id:
            self.datetime = timezone.now()
            just_created = True
        super(Review, self).save(*args, **kwargs)
        if just_created:
            ReviewActivity.objects.create(user=self.posted_by, course=self.course, review=self)

    def __unicode__(self):
        return str(self.review)

DOC_ACCESS_LEVEL_PUBLIC = 1
DOC_ACCESS_LEVEL_SAME_COURSE = 2
DOC_ACCESS_LEVEL_PRIVATE = 3

DOC_ACCESS_LEVELS = (
    (DOC_ACCESS_LEVEL_PUBLIC, "Everyone"),
    (DOC_ACCESS_LEVEL_SAME_COURSE, "Only the participants of this course (module)"),
    (DOC_ACCESS_LEVEL_PRIVATE, "Only me")
)

class CourseDocument(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, null=True, blank=True)
    document = models.FileField(upload_to='course/documents/')
    course_topic = models.ForeignKey('CourseTopic', null=True, related_name="documents")
    course = models.ForeignKey('Course', related_name="documents")
    course_module = models.ForeignKey('CourseModule', related_name="documents", null=True)
    submitter = models.ForeignKey('jUser')
    submit_time = models.DateTimeField(default=timezone.now())

    # Allow people who are not registered for the course to see this document?
    access = models.IntegerField(choices=DOC_ACCESS_LEVELS,default=DOC_ACCESS_LEVEL_PUBLIC)

    def __unicode__(self):
        return str(self.name)
    def can_view(self,user):
        access = self.access

        if access == DOC_ACCESS_LEVEL_PUBLIC:
            return True
        elif access == DOC_ACCESS_LEVEL_SAME_COURSE:
            course = self.course
            if self.course_module_id is None:
                return user.is_participant_of(course)
            else:
                is_student = self.course_module.students.filter(studentcourseregistration__student=user).exists()
                is_manager = user.is_professor_of(course) or user.is_assistant_of(course)
                return is_student or is_manager
        elif access == DOC_ACCESS_LEVEL_PRIVATE:
            return user.id == self.submitter_id
        else:
            raise Exception("Invalid access level (%d) for document (%s)" % (access, self.name))



    def save(self, *args, **kwargs):
        just_created = False
        if not self.id:
            just_created = True
        super(CourseDocument, self).save(*args, **kwargs)
        if just_created:
            DocumentActivity.objects.create(user=self.submitter, course=self.course, document=self)

HOMEWORK_MIN_FILES = 1
HOMEWORK_MAX_FILES = 10

class CourseHomeworkRequest(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, null=True, blank=True)
    course = models.ForeignKey('Course')
    deadline = models.ForeignKey('Deadline')
    submitter = models.ForeignKey('jUser')
    course_topic = models.ForeignKey('CourseTopic', related_name="homework_requests", null=True, blank=True)
    number_files = models.IntegerField(default=1, validators=[MinValueValidator(HOMEWORK_MIN_FILES),
                                                              MaxValueValidator(HOMEWORK_MAX_FILES)])
    is_published = models.BooleanField(default=False)
    document = models.ForeignKey('CourseDocument', related_name='homework_requests', null=True, blank=True)
    course_module = models.ForeignKey('CourseModule', related_name='homework_requests', null=True)
    def save(self, *args, **kwargs):
        just_created = False
        if not self.id:
            just_created = True
        super(CourseHomeworkRequest, self).save(*args, **kwargs)
        if just_created:
            HomeworkActivity.objects.create(user=self.submitter, course=self.course, homework=self)

    def delete(self, *args, **kwargs):
        deadline = self.deadline
        super(CourseHomeworkRequest, self).delete(*args, **kwargs)
        deadline.delete()

    def can_view(self,user):
        user_courses = user.courses_assisted.all() | user.courses_managed.all()
        is_ta_or_prof = user_courses.filter(id=self.course_id).exists()
        is_student_same_module = None
        if self.course_module is not None:
            is_student_same_module = self.course_module.students.filter(id=user.id).exists()
        else:
            is_student_same_module = user.is_student_of(self.course)
        return is_ta_or_prof or is_student_same_module

    @staticmethod
    def filter_qs_by_permission_to_view(qs,user):
        user_courses = user.courses_assisted.all() | user.courses_managed.all()
        if self.course_module_id is None:
            user_courses |= user.courses_enrolled.all()
            return qs.filter(course__in=user_courses)
        else:
            module_students = self.course_module.students.all()
            return qs.filter(Q(Q(course__in=user_courses) | Q(user__in=module_students)))



    def __unicode__(self):
        return str(self.name)

class CourseHomeworkSubmission(models.Model):
    homework_request = models.ForeignKey('CourseHomeworkRequest')
    document = models.FileField(upload_to='course/homework/')

    course = models.ForeignKey('Course')
    submitter = models.ForeignKey('jUser')
    submit_time = models.DateTimeField()
    name = models.CharField(max_length=200)
    file_number = models.IntegerField(default=1, validators=[MinValueValidator(HOMEWORK_MIN_FILES),
                                                             MaxValueValidator(HOMEWORK_MAX_FILES)])

    def save(self, *args, **kwargs):
        if not self.id:
            self.submit_time = timezone.now()
        self.name = slugify(self.submitter.first_name + "_" + self.submitter.last_name + " " + self.homework_request.name + " (" + str(self.file_number) + ")")
        super(CourseHomeworkSubmission, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        grade = None
        if hasattr(self, 'grade'):
            grade = self.grade
        super(CourseHomeworkSubmission, self).delete(*args, **kwargs)
        if grade:
            grade.delete()

    def __unicode__(self):
        return str(self.name)

class CourseHomeworkGrade(models.Model):
    submitter = models.ForeignKey('jUser', related_name='homework_graded')
    student = models.ForeignKey('jUser', related_name='grades')
    homework_request = models.ForeignKey('CourseHomeworkRequest')
    file_number = models.IntegerField(default=1, validators=[MinValueValidator(HOMEWORK_MIN_FILES),
                                                             MaxValueValidator(HOMEWORK_MAX_FILES)])

    is_published = models.BooleanField(default=False)
    grade = models.FloatField(default=0.0, validators=[MinValueValidator(0.0),
                                                       MaxValueValidator(100.0)])

    submission = models.OneToOneField('CourseHomeworkSubmission', related_name='grade', null=True, blank=True)

    def __unicode__(self):
        return str(self.grade)



###########################################################################
############################ Forums, Wikis ################################
###########################################################################

FORUM_GENERAL = "1"
FORUM_COURSE = "2"
FORUM_TYPES = (
    (FORUM_GENERAL, 'General Forum'),
    (FORUM_COURSE, 'Course Forum'),
)

class Forum(models.Model):
    forum_type = models.CharField(max_length=1, choices=FORUM_TYPES, default=FORUM_COURSE)

    def get_tags(self):
        if self.forum_type == FORUM_GENERAL:
            return self.forumgeneral.get_tags()
        elif self.forum_type == FORUM_COURSE:
            return self.forumcourse.get_tags()
        return None

    def get_tags_names(self):
        if self.forum_type == FORUM_GENERAL:
            return self.forumgeneral.get_tags_names()
        elif self.forum_type == FORUM_COURSE:
            return self.forumcourse.get_tags_names()
        return None

    def get_view_tags(self, user):
        if self.forum_type == FORUM_GENERAL:
            return self.forumgeneral.get_view_tags(user)
        elif self.forum_type == FORUM_COURSE:
            return self.forumcourse.get_view_tags(user)
        return None

    def get_post_tags(self, user):
        if self.forum_type == FORUM_GENERAL:
            return self.forumgeneral.get_post_tags(user)
        elif self.forum_type == FORUM_COURSE:
            return self.forumcourse.get_post_tags(user)
        return None

    def get_answer_tags(self, user):
        if self.forum_type == FORUM_GENERAL:
            return self.forumgeneral.get_answer_tags(user)
        elif self.forum_type == FORUM_COURSE:
            return self.forumcourse.get_answer_tags(user)
        return None

    def get_new_post_url(self):
        if self.forum_type == FORUM_GENERAL:
            return reverse('forum_new_post_general')
        elif self.forum_type == FORUM_COURSE:
            return reverse('forum_new_post_course', args=[self.forumcourse.course.slug])
        return ""

    def __unicode__(self):
        return "Forum"


class ForumGeneral(Forum):
    def get_tags(self):
        general_tags = list(ForumTag.objects.filter(tag_type=FORUMTAG_GENERAL))
        return general_tags

    def get_tags_names(self):
        return [tag.name for tag in self.get_tags()]

    def get_view_tags(self, user):
        return self.get_tags()

    def get_post_tags(self, user):
        return self.get_tags()

    def get_answer_tags(self, user):
        return self.get_tags()

class ForumCourse(Forum):
    course = models.OneToOneField('Course', related_name="forum")

    def get_tags(self):
        primary_tags = list(ForumTag.objects.filter(tag_type=FORUMTAG_PRIMARY))
        topic_tags = list(self.forumtopictag_set.all())
        extra_tags = list(self.forumextratag_set.all())
        return primary_tags + topic_tags + extra_tags


    def get_tags_names(self):
        return [tag.name for tag in self.get_tags()]

    def get_view_tags(self, user):
        tags = self.get_tags()

        view_tags = []
        for tag in tags:
            if tag.can_view(user, self.course):
                view_tags.append(tag)
        return view_tags

    def get_post_tags(self, user):
        tags = self.get_tags()

        post_tags = []
        for tag in tags:
            if tag.can_post(user, self.course):
                post_tags.append(tag)
        return post_tags

    def get_answer_tags(self, user):
        tags = self.get_tags()

        answer_tags = []
        for tag in tags:
            if tag.can_answer(user, self.course):
                answer_tags.append(tag)
        return answer_tags

    def __unicode__(self):
        return str(self.course)


FORUMTAG_PRIMARY = "1"
FORUMTAG_TOPIC = "2"
FORUMTAG_EXTRA = "3"
FORUMTAG_GENERAL = "5"
FORUMTAG_TYPES = (
    (FORUMTAG_PRIMARY, 'Primary Tag'),
    (FORUMTAG_TOPIC, 'Topic Tag'),
    (FORUMTAG_EXTRA, 'Extra Tag'),
    (FORUMTAG_GENERAL, 'General Tag')
)

# General Forum tags
ForumGeneralTags = ['event', 'reportbug', 'suggestfeature', 'EECS', 'Life', 'Logistics', 'Math', 'NatEnv', 'Econ', 'History', 'Humanities', 'Law', 'Psych', 'Social', 'Stats', 'USC', 'FY', "Colloquia", "Humanities", "Languages", "Undergrad", "Grad", "Fall", "Spring", "SES", "SHSS"]
# Course Forum tags
PublicForumTags = ['general']
StudentViewTags = ['general', 'announcement', 'meta', 'offtopic', 'noprof'] # + topic and extra tags
StudentPostTags = ['general', 'askprof', 'meta', 'offtopic', 'noprof'] # + topic and extra tags
StudentAnswerTags = ['general', 'announcement', 'meta', 'offtopic', 'noprof'] # + topic and extra tags
ProfessorViewTags = ['general', 'announcement', 'askprof', 'meta', 'offtopic'] # + topic and extra tags
ProfessorPostTags = ['general', 'announcement', 'askprof', 'meta', 'offtopic'] # + topic and extra tags
ProfessorAnswerTags = ['general', 'announcement', 'askprof', 'meta', 'offtopic'] # + topic and extra tags
AdminViewTags = ['general', 'announcement', 'meta']
AdminPostTags = ['general', 'announcement', 'meta']
AdminAnswerTags = ['general', 'announcement', 'meta']
# Extra permissions: Anyone can view and answer their own posts

class ForumTag(models.Model):
    name = models.CharField(max_length=20)
    tag_type = models.CharField(max_length=1, default=FORUMTAG_EXTRA)

    def can_view(self, user, course=None):
        if self.tag_type == FORUMTAG_TOPIC or self.tag_type == FORUMTAG_EXTRA:
            return user.is_student_of(course) or user.is_professor_of(course)
        if self.tag_type == FORUMTAG_GENERAL:
            return self.name in ForumGeneralTags

        if self.name in PublicForumTags:
            return True

        if user.is_student_of(course):
            return (self.name in StudentViewTags)
        elif user.is_professor_of(course):
            return (self.name in ProfessorViewTags)
        elif user.is_admin_of(course):
            return (self.name in AdminViewTags)
        return False

    def can_post(self, user, course=None):
        if self.tag_type == FORUMTAG_TOPIC or self.tag_type == FORUMTAG_EXTRA:
            return user.is_student_of(course) or user.is_professor_of(course)
        if self.tag_type == FORUMTAG_GENERAL:
            return self.name in ForumGeneralTags

        if self.name in PublicForumTags:
            return True

        if user.is_student_of(course):
            return (self.name in StudentPostTags)
        elif user.is_professor_of(course):
            return (self.name in ProfessorPostTags)
        elif user.is_admin_of(course):
            return (self.name in AdminPostTags)
        return False

    def can_answer(self, user, course=None):
        if self.tag_type == FORUMTAG_TOPIC or self.tag_type == FORUMTAG_EXTRA:
            return user.is_student_of(course) or user.is_professor_of(course)
        if self.tag_type == FORUMTAG_GENERAL:
            return self.name in ForumGeneralTags

        if self.name in PublicForumTags:
            return True

        if user.is_student_of(course):
            return (self.name in StudentAnswerTags)
        elif user.is_professor_of(course):
            return (self.name in ProfessorAnswerTags)
        elif user.is_admin_of(course):
            return (self.name in AdminAnswerTags)
        return False


    @staticmethod
    def create_tag_name(name):
        clean_name = re.sub('[.!,;]', '', name)
        clean_name = re.sub('-_', ' ', clean_name)
        words = clean_name.title().split(' ')
        tag_name = ""
        for word in words:
            tag_name += word[0:3]
        return tag_name[0:20]

    def __unicode__(self):
        return str(self.name)

class ForumTopicTag(ForumTag):
    topic = models.OneToOneField('CourseTopic', primary_key=True)
    forum = models.ForeignKey('Forum')

    def __unicode__(self):
        return str(self.name)

class ForumExtraTag(ForumTag):
    forum = models.ForeignKey('Forum')

    def __unicode__(self):
        return str(self.name)


class ForumPost(models.Model):
    name = models.CharField(max_length=250)
    forum = models.ForeignKey('Forum')
    text = models.CharField(max_length=5000, blank=True, null=True)
    datetime = models.DateTimeField()

    tag = models.ForeignKey('ForumTag')

    posted_by = models.ForeignKey('jUser', related_name='question_posted')
    anonymous = models.BooleanField(default=False)

    upvoted_by = models.ManyToManyField('jUser', related_name='question_upvoted')
    downvoted_by = models.ManyToManyField('jUser', related_name='question_downvoted')

    followed_by = models.ManyToManyField('jUser', related_name='posts_following')

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        just_created = False
        if not self.id:
            self.datetime = timezone.now()
            just_created = True
        super(ForumPost, self).save(*args, **kwargs)
        if just_created:
            ForumPostActivity.objects.create(user=self.posted_by, forum_post = self)
        if self.forum.forum_type == FORUM_GENERAL:
            self.followed_by.add(self.posted_by)
        elif self.forum.forum_type == FORUM_COURSE:
            course = self.forum.forumcourse.course
            user = self.posted_by
            if not (user.is_professor_of(course) or user.is_student_of(course)):
                self.followed_by.add(user)

    def get_absolute_url(self):
        if self.forum.forum_type == FORUM_GENERAL:
            return reverse('forum_general', args=()) + "?post=%s" % self.id
        else: # FORUM_COURSE
            return reverse('forum_course', args=(self.forum.forumcourse.course.slug,)) + "?post=%s" % self.id



class ForumAnswer(models.Model):
    post = models.ForeignKey('ForumPost')
    text = models.CharField(max_length=5000)
    datetime = models.DateTimeField()

    parent_answer = models.ForeignKey('ForumAnswer', null=True, blank=True)

    posted_by = models.ForeignKey('jUser', related_name='answer_posted')
    anonymous = models.BooleanField(default=False)

    upvoted_by = models.ManyToManyField('jUser', related_name='answer_upvoted')
    downvoted_by = models.ManyToManyField('jUser', related_name='answer_downvoted')

    def __unicode__(self):
        return self.text

    def save(self, *args, **kwargs):
        just_created = False
        if not self.id:
            self.datetime = timezone.now()
            just_created = True
        super(ForumAnswer, self).save(*args, **kwargs)
        if just_created:
            ForumAnswerActivity.objects.create(user=self.posted_by, forum_answer=self)
        

class WikiContributions(models.Model):
    user = models.ForeignKey('jUser')
    wiki = models.ForeignKey('WikiPage')
    revision = models.ForeignKey('versioning.Revision')

    def save(self, *args, **kwargs):
        super(WikiContributions, self).save(*args, **kwargs)
        WikiActivity.objects.create(user=self.user, course=self.wiki.course, contribution=self)

    def __unicode__(self):
        return "Contribution " + self.user.username


class WikiPage(models.Model):
    course = models.OneToOneField('Course', related_name='wiki')
    content = models.TextField()

    def __unicode__(self):
        return "Wiki " + str(self.course.name)

    def get_absolute_url(self):
        return reverse('app.wiki.views.view_wiki_page', args=[self.course.slug])



versioning.register(
    WikiPage,
    ['content']
)


###########################################################################
############################### Schedule ##################################
###########################################################################

class Appointment(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    location = models.CharField(max_length=250, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)

class PersonalAppointment(Appointment):
    user = models.ForeignKey('jUser',related_name='appointments')
    def __unicode__(self):
        return str(self.user)

class CourseAppointment(Appointment):
    course = models.ForeignKey('Course',related_name='appointments')
    course_topic = models.ForeignKey('CourseTopic', related_name='appointments', null= True)
    course_module = models.ForeignKey('CourseModule', related_name='appointments', null=True)
    def __unicode__(self):
        return self.course.name


###########################################################################
############################### NewsFeed ##################################
###########################################################################

class Activity(models.Model):
    timestamp = models.DateTimeField()
    user = models.ForeignKey('jUser') # The user who performed the action

    def get_type(self):
        if hasattr(self, 'generalactivity'):
            general_activity = self.generalactivity
            if hasattr(general_activity, 'forumpostactivity'):
                return "ForumPostActivity"
            elif hasattr(general_activity, 'forumansweractivity'):
                return "ForumAnswerActivity"
            else:
                return "GeneralActivity"
        elif hasattr(self,'courseactivity'):
            course_activity = self.courseactivity
            if hasattr(course_activity, 'homeworkactivity'):
                return "HomeworkActivity"
            elif hasattr(course_activity, 'documentactivity'):
                return "DocumentActivity"
            elif hasattr(course_activity, 'reviewactivity'):
                return "ReviewActivity"
            elif hasattr(course_activity, 'wikiactivity'):
                return "WikiActivity"
            else:
                return "CourseActivity"

    def get_instance(self):

        if hasattr(self, 'generalactivity'):
            general_activity = self.generalactivity
            if hasattr(general_activity, 'forumpostactivity'):
                return general_activity.forumpostactivity
            elif hasattr(general_activity, 'forumansweractivity'):
                return general_activity.forumansweractivity
            else:
                return general_activity
        elif hasattr(self,'courseactivity'):
            course_activity = self.courseactivity
            if hasattr(course_activity, 'homeworkactivity'):
                return course_activity.homeworkactivity
            elif hasattr(course_activity, 'documentactivity'):
                return course_activity.documentactivity
            elif hasattr(course_activity, 'reviewactivity'):
                return course_activity.reviewactivity
            elif hasattr(course_activity, 'wikiactivity'):
                return course_activity.wikiactivity
            else:
                return course_activity

    def can_view(self,user):
        activity_type = self.get_type()
        instance = self.get_instance()
        if activity_type == "ForumPostActivity":
            tag = instance.forum_post.tag
            return tag.can_view(user, instance.get_course())
        elif activity_type == "ForumAnswerActivity":
            tag = instance.forum_answer.post.tag
            return tag.can_view(user, instance.get_course())
        elif activity_type == "HomeworkActivity":
            return instance.homework.can_view(user)
        elif activity_type == "DocumentActivity":
            return instance.document.can_view(user)
        else:
            return True



    def save(self, *args, **kwargs):
        if not self.id:
            activity_type = self.get_type()
            instance = self.get_instance()
            if activity_type == "ReviewActivity":
                self.timestamp = instance.review.datetime
            elif activity_type == "ForumPostActivity":
                self.timestamp = instance.forum_post.datetime
            elif activity_type == "ForumAnswerActivity":
                self.timestamp = instance.forum_answer.datetime
            elif activity_type == "DocumentActivity":
                self.timestamp = instance.document.submit_time
            else:
                self.timestamp = timezone.now()
        super(Activity, self).save(*args, **kwargs)

    @staticmethod
    def course_page_activities(course, course_module=None):
        course_module_id = course_module.id if course_module is not None else None
        return Activity.objects.filter(Q(
            Q(courseactivity__course=course)
            | 
            Q(generalactivity__forumpostactivity__forum_post__forum__forum_type=FORUM_COURSE, 
                generalactivity__forumpostactivity__forum_post__forum__forumcourse__course=course) 
            | 
            Q(generalactivity__forumansweractivity__forum_answer__post__forum__forum_type=FORUM_COURSE, 
                generalactivity__forumansweractivity__forum_answer__post__forum__forumcourse__course=course)
            )).distinct().order_by('-timestamp')

    @staticmethod
    def dashboard_page_activities(user):
        user_courses = user.courses_enrolled.all() | user.courses_managed.all() | user.courses_assisted.all()
        user_module_ids = [u['id'] for u in user.course_modules.all().values('id')]
        return Activity.objects.filter(
            Q(
                # Course Activities
                Q(courseactivity__course__in = user_courses)                   
                |
                Q(  # Forum Post Activities
                    Q(  # Posts in forums of current user's courses
                        Q(generalactivity__forumpostactivity__forum_post__forum__forum_type=FORUM_COURSE),
                        Q(generalactivity__forumpostactivity__forum_post__forum__forumcourse__course__in = user_courses)          
                    )
                    |  # Posts the user is following
                    Q ( generalactivity__forumpostactivity__forum_post__followed_by = user )
                )
                |
                Q( # Forum Answer Activities
                    Q(  # Answers to posts from course forums that belong to user's courses
                        Q(generalactivity__forumansweractivity__forum_answer__post__forum__forum_type = FORUM_COURSE), 
                        Q(generalactivity__forumansweractivity__forum_answer__post__forum__forumcourse__course__in = user_courses )      
                    )
                    | # Answers to posts the user is following
                    Q ( generalactivity__forumansweractivity__forum_answer__post__followed_by = user )
                )        
            ), 
            ~Q(user=user) ).distinct().order_by('-timestamp')
    @staticmethod
    def profile_page_activities(user):
        activities = Activity.objects.filter(user=user)
        activities = activities.filter(
            ~Q(generalactivity__forumpostactivity__forum_post__anonymous=True),
            ~Q(generalactivity__forumansweractivity__forum_answer__anonymous=True),
            ~Q(courseactivity__reviewactivity__review__anonymous=True)
        ).distinct()
        
        return activities.order_by('-timestamp')


class GeneralActivity(Activity):
    pass

# Base class for all activities
class CourseActivity(Activity):
    course = models.ForeignKey('Course', related_name="activities")
    def __unicode__(self):
        return self.get_type() + " Object"

    

# When a user creates a new post
class ForumPostActivity(GeneralActivity):
    forum_post = models.ForeignKey('ForumPost')

    def get_course(self):
        forum = self.forum_post.forum
        if forum.forum_type == FORUM_COURSE:
            return forum.forumcourse.course
        else:
            return None

# When a user answers to a post you are following
class ForumAnswerActivity(GeneralActivity):
    forum_answer = models.ForeignKey('ForumAnswer')

    def get_course(self):
        forum = self.forum_answer.post.forum
        if forum.forum_type == FORUM_COURSE:
            return forum.forumcourse.course
        else:
            return None

# When a user (prof/TA) posts a new homework
class HomeworkActivity(CourseActivity):
    homework = models.ForeignKey('CourseHomeworkRequest')

# When a user uploads a new document11
class DocumentActivity(CourseActivity): 
    document = models.ForeignKey('CourseDocument')


# When a user writes a review for a course
class ReviewActivity(CourseActivity):
    review = models.ForeignKey('Review')

# When a user makes a wiki change
class WikiActivity(CourseActivity):
    contribution = models.ForeignKey('WikiContributions')



## SUBSCRIBERS ###

class Subscriber(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
