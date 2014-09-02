from datetime import * #datetime
import pytz # timezones
from django.utils import timezone
import versioning
import re 

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.conf import settings 
from django.core.urlresolvers import reverse
from django import forms


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
        name,extension = filename.split(".")
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
        registration = StudentCourseRegistration.objects.filter(student=self, course=course)
        return self.is_student() and registration and registration[0].is_approved

    def is_professor_of(self, course):
        if not self.is_professor():
            return False
        registration = ProfessorCourseRegistration.objects.filter(professor=self, course=course)
        return registration and registration[0].is_approved

    def is_admin_of(self, course):
        if not self.is_admin():
            return False
        categories = self.categories_managed.all()
        for category in categories:
            if course in category.get_all_courses():
                return True
        return False


    def __unicode__(self):
        return str(self.username)


class StudentCourseRegistration(models.Model):
    student = models.ForeignKey('jUser')
    course = models.ForeignKey('Course')
    is_approved = models.BooleanField(default = False) # True if registration is approved

    def __unicode__(self):
        return str(self.student)

class ProfessorCourseRegistration(models.Model):
    professor = models.ForeignKey('jUser')
    course = models.ForeignKey('Course')
    is_approved = models.BooleanField(default = False) # True if registration is approved

    def __unicode__(self):
        return str(self.professor)









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

    def save(self, *args, **kwargs):
        original_slug = slugify(self.name)
        slug = original_slug
        appendix = 1
        while Course.objects.filter(slug = slug).count() > 0:
            slug = original_slug + "-" + str(appendix)
            appendix += 1
        self.slug = slug
        super(Course, self).save(*args, **kwargs)
        Forum.objects.get_or_create(course=self)

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
        if not len(tags):
            tag_name = ForumTag.create_tag_name(self.name)
            ForumTopicTag.objects.create(name=tag_name, tag_type=FORUMTAG_TOPIC, \
                forum=Forum.objects.get(pk=self.course.id), topic=self)
        else:
            tag = tags[0]
            tag.name = ForumTag.create_tag_name(self.name)
            tag.save()
        super(CourseTopic, self).save(*args, **kwargs)

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
    # need to change the field above to non-nullable.
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

class CourseDocument(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, null=True, blank=True)
    document = models.FileField(upload_to='course/documents/')
    course_topic = models.ForeignKey('CourseTopic', null=True, related_name="documents")
    course = models.ForeignKey('Course', related_name="documents")
    submitter = models.ForeignKey('jUser')
    submit_time = models.DateTimeField()

    def __unicode__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if not self.id:
            self.submit_time = timezone.now()
        super(CourseDocument, self).save(*args, **kwargs)
        DocumentActivity.objects.create(user=self.submitter, course=self.course, document=self)

class CourseHomeworkRequest(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, null=True, blank=True)
    deadline = models.ForeignKey('Deadline')
    course_topic = models.ForeignKey('CourseTopic', related_name="homework_requests", null=True, blank=True)
    course = models.ForeignKey('Course')
    submitter = models.ForeignKey('jUser')

    def delete(self, *args, **kwargs):
        deadline = self.deadline
        super(CourseHomeworkRequest, self).save(*args, **kwargs)
        deadline.delete()

    def __unicode__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        super(CourseHomeworkRequest, self).save(*args, **kwargs)
        HomeworkActivity.objects.create(user=self.submitter, course=self.course, homework=self)

class CourseHomeworkSubmission(models.Model):
    homework_request = models.ForeignKey('CourseHomeworkRequest')
    document = models.FileField(upload_to='course/homework/')

    course = models.ForeignKey('Course')
    submitter = models.ForeignKey('jUser')
    submit_time = models.DateTimeField()
    name = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        if not self.id:
            self.submit_time = timezone.now()
        self.name = slugify(self.submitter.first_name + "-" + self.submitter.last_name + "-" + self.homework_request.name)
        super(CourseHomeworkSubmission, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.name)

###########################################################################
############################ Forums, Wikis ################################
###########################################################################

class Forum(models.Model):
    course = models.OneToOneField('Course', primary_key=True)

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
            if tag.can_view(self.course, user):
                view_tags.append(tag)
        return view_tags

    def get_post_tags(self, user):
        tags = self.get_tags()

        post_tags = []
        for tag in tags:
            if tag.can_post(self.course, user):
                post_tags.append(tag)
        return post_tags

    def get_answer_tags(self, user):
        tags = self.get_tags()

        answer_tags = []
        for tag in tags:
            if tag.can_answer(self.course, user):
                answer_tags.append(tag)
        return answer_tags

    def __unicode__(self):
        return str(self.course)


FORUMTAG_PRIMARY = "1"
FORUMTAG_TOPIC = "2"
FORUMTAG_EXTRA = "3"
FORUMTAG_TYPES = (
    (FORUMTAG_PRIMARY, 'Primary Tag'),
    (FORUMTAG_TOPIC, 'Topic Tag'),
    (FORUMTAG_EXTRA, 'Extra Tag'),
)

PublicForumTags = ['general']
StudentViewTags = ['general', 'announcement', 'meta', 'offtopic']
StudentPostTags = ['general', 'askprof', 'meta', 'offtopic']
StudentAnswerTags = ['general', 'announcement', 'meta', 'offtopic']
ProfessorViewTags = ['general', 'announcement', 'askprof', 'meta', 'offtopic']
ProfessorPostTags = ['general', 'announcement', 'askprof', 'meta', 'offtopic']
ProfessorAnswerTags = ['general', 'announcement', 'askprof', 'meta', 'offtopic']
AdminViewTags = ['general', 'announcement', 'meta']
AdminPostTags = ['general', 'announcement', 'meta']
AdminAnswerTags = ['general', 'announcement', 'meta']
# Extra permissions: Anyone can view and answer their own posts

class ForumTag(models.Model):
    name = models.CharField(max_length=20)
    tag_type = models.CharField(max_length=1, default=FORUMTAG_EXTRA)

    def can_view(self, course, user):
        if self.name in PublicForumTags:
            return True

        if user.is_student_of(course):
            return (self.name in StudentViewTags) if self.tag_type == FORUMTAG_PRIMARY else True
        elif user.is_professor_of(course):
            return (self.name in ProfessorViewTags) if self.tag_type == FORUMTAG_PRIMARY else True
        elif user.is_admin_of(course):
            return (self.name in AdminViewTags) if self.tag_type == FORUMTAG_PRIMARY else False
        return False

    def can_post(self, course, user):
        if self.name in PublicForumTags:
            return True

        if user.is_student_of(course):
            return (self.name in StudentPostTags) if self.tag_type == FORUMTAG_PRIMARY else True
        elif user.is_professor_of(course):
            return (self.name in ProfessorPostTags) if self.tag_type == FORUMTAG_PRIMARY else True
        elif user.is_admin_of(course):
            return (self.name in AdminPostTags) if self.tag_type == FORUMTAG_PRIMARY else False
        return False

    def can_answer(self, course, user):
        if self.name in PublicForumTags:
            return True

        if user.is_student_of(course):
            return (self.name in StudentAnswerTags) if self.tag_type == FORUMTAG_PRIMARY else True
        elif user.is_professor_of(course):
            return (self.name in ProfessorAnswerTags) if self.tag_type == FORUMTAG_PRIMARY else True
        elif user.is_admin_of(course):
            return (self.name in AdminAnswerTags) if self.tag_type == FORUMTAG_PRIMARY else False
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
        if not self.id:
            self.datetime = timezone.now()
        super(ForumPost, self).save(*args, **kwargs)
        ForumPostActivity.objects.create(user=self.posted_by, course=self.forum.course, forum_post=self)
        self.followed_by.add(self.posted_by)

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
        if not self.id:
            self.datetime = timezone.now()
        super(ForumAnswer, self).save(*args, **kwargs)
        ForumAnswerActivity.objects.create(user=self.posted_by, course=self.post.forum.course, 
                                            forum_answer=self)
        self.post.followed_by.add(self.posted_by)
        

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

    def can_edit(self, user):
        return user.is_student_of(self.course) or user.is_professor_of(self.course)


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
    course_topic = models.ForeignKey('CourseTopic', related_name='appointments')
    def __unicode__(self):
        return self.course.name


###########################################################################
############################### NewsFeed ##################################
###########################################################################

# Base class for all activities
class CourseActivity(models.Model):
    timestamp = models.DateTimeField()
    course = models.ForeignKey('Course', related_name="activities")
    user = models.ForeignKey('jUser') # The user who performed the action

    def get_subclass_type(self):
        if hasattr(self,'forumpostactivity'):
            return "ForumPostActivity"
        elif hasattr(self, 'forumansweractivity'):
            return "ForumAnswerActivity"
        elif hasattr(self, 'homeworkactivity'):
            return "HomeworkActivity"
        elif hasattr(self, 'documentactivity'):
            return "DocumentActivity"
        elif hasattr(self, 'reviewactivity'):
            return "ReviewActivity"
        elif hasattr(self, 'wikiactivity'):
            return "WikiActivity"
        else:
            return "CourseActivity"

    def can_view(self,user):
        activity_type = self.get_subclass_type()
        if activity_type != "ForumPostActivity" and activity_type != "ForumAnswerActivity":
            return True
        elif activity_type == "ForumPostActivity":
            tag = self.forumpostactivity.forum_post.tag
            if tag.can_view(self.course,user):
                return True
            else:
                return False
        else:
            # activity_type == ForumAnswerActivity
            tag = self.forumansweractivity.forum_answer.post.tag
            if tag.can_view(self.course,user):
                return True
            else:
                return False

    def __unicode__(self):
        return self.get_subclass_type() + " Object"

    def save(self, *args, **kwargs):
        if not self.id:
            self.timestamp = timezone.now()
        super(CourseActivity, self).save(*args, **kwargs)

# When a user creates a new post
class ForumPostActivity(CourseActivity):
    forum_post = models.ForeignKey('ForumPost')

# When a user answers to a post you are following
class ForumAnswerActivity(CourseActivity):
    forum_answer = models.ForeignKey('ForumAnswer')

# When a user (prof/TA) posts a new homework
class HomeworkActivity(CourseActivity):
    homework = models.ForeignKey('CourseHomeworkRequest')

# When a user uploads a new document
class DocumentActivity(CourseActivity): 
    document = models.ForeignKey('CourseDocument')

# When a user writes a review for a course
class ReviewActivity(CourseActivity):
    review = models.ForeignKey('Review')

# When a user makes a wiki change
class WikiActivity(CourseActivity):
    contribution = models.ForeignKey('WikiContributions')