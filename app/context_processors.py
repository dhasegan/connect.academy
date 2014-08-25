from django.template.loader import render_to_string
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


from app.models import *
from app.ratings import *
from app.forum.context_processors import *


def debug(context):
    return {
        'DEBUG': settings.DEBUG
    }


def user_authenticated(request):
    context = {}
    if request.user and request.user.is_authenticated():
        user = request.user
        context["user_auth"] = jUser.objects.get(id=user.id)
        if not user.is_active:
            if not user.email or user.email == "":
                context['warning'] = render_to_string('objects/notifications/auth/email_not_set.html', {})
            else:
                context['warning'] = render_to_string('objects/notifications/auth/email_not_activated.html', {})

    return context

def activity_context(activity, current_user):
    activity_context = {
        "type": activity.get_subclass_type(),
        "activity": activity,
    }
    if hasattr(activity,"forumpostactivity"):
        activity_context["post"] = forum_post_context(activity.forumpostactivity.forum_post, current_user)
    elif hasattr(activity, "forumansweractivity"):
        answer = activity.forumansweractivity.forum_answer
        activity_context["answer"] = forum_answer_context(answer.post, answer, current_user)
    elif hasattr(activity, "homeworkactivity"):
        nr_students = StudentCourseRegistration.objects.filter(course=activity.course, 
                                                                is_approved=True).count()
        current_time = pytz.utc.localize(datetime.now())
        hw = activity.homeworkactivity.homework
        course = activity.course
        within_deadline = hw.deadline.start <= current_time and current_time < hw.deadline.end
        is_allowed = course.get_registration_status(current_user) == COURSE_REGISTRATION_REGISTERED
        is_student = current_user.is_student_of(course)
        can_submit_homework = is_student and is_allowed and within_deadline
        
        homework_submission = None
        homework_submissions = CourseHomeworkSubmission.objects.filter(submitter=current_user, homework_request=hw)
        if homework_submissions:
            homework_submission = homework_submissions[0]

        homework_submitted = hw.coursehomeworksubmission_set.all().count()

        activity_context["homework"] = {
            "homework": hw,
            "can_submit": can_submit_homework,
            "is_allowed": is_allowed,
            "previous_submission": homework_submission,
            "stats": {
                "submitted": homework_submitted,
                "students": nr_students
            }
        }
    return activity_context

def dashboard_activities(request,user):


    own_course_activities = list(CourseActivity.objects.filter(
        Q(course__in=list(user.courses_enrolled.all()) + list(user.courses_managed.all())), ~Q(user=user)).reverse())

    # get all answers to posts that the user is following, except those in the users's own courses,
    # to avoid duplication
    #
    forum_answer_activities = list(ForumAnswerActivity.objects.filter(
        Q(forum_answer__post__in=user.posts_following.all()), ~Q(user=user)).exclude(
            forum_answer__post__forum__course__in=list(user.courses_enrolled.all()) + list(user.courses_managed.all())).reverse())

    activities_list = sorted(own_course_activities + forum_answer_activities,
                             key=lambda activity: activity.timestamp,
                             reverse=True)

    activities_context = [activity_context(activity,user) for activity in activities_list]

  
    return paginated(request,activities_context, 20)


def paginated(request, objects_list, per_page):
    paginator = Paginator(objects_list, per_page) # 20 activities per page

    page = request.GET.get('page')
    try:
        objects = paginator.page(page).object_list
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        objects = paginator.page(1).object_list
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        objects = []

    return objects



def dashboard_context(request):
    user = jUser.objects.get(id=request.user.id)

    context = {
        'courses': [],
        'schedule_items': [],
        'user': user,
        'hw_redirect_url': '/home'
    }

    registrations = StudentCourseRegistration.objects.filter(student=user)
    for reg in registrations:
        context['courses'].append({'course': reg.course, 'is_approved': reg.is_approved, 'homework': []})

    registrations = ProfessorCourseRegistration.objects.filter(professor=user)
    for reg in registrations:
        context['courses'].append({'course': reg.course, 'is_approved': reg.is_approved, 'homework': []})


    today =  datetime.combine(date.today(), datetime.min.time())
    tomorrow = today + timedelta(days=1)
    schedule_items = list(CourseAppointment.objects.filter(course__students=user,
                            start__gte=pytz.utc.localize( today ),
                            start__lte=pytz.utc.localize( tomorrow ))) +\
                        list(PersonalAppointment.objects.filter(user=user,
                            start__gte=pytz.utc.localize( today ),
                            start__lte=pytz.utc.localize( tomorrow )))

    context['schedule_items'] = schedule_items

    for reg in context['courses']:
        if reg['is_approved']:
            course_hw = reg['course'].coursehomeworkrequest_set
            for homework in course_hw.filter(deadline__end__gte=pytz.utc.localize(datetime.now())):
                homework_submitted = CourseHomeworkSubmission.objects.filter(submitter=user,
                                                                             homework_request=homework).count() > 0
                reg['homework'].append({'submitted': homework_submitted,
                                        'hw': homework})

    context['forum_posts'] = ForumPost.objects.filter(posted_by=user).reverse()

    context['activities'] = dashboard_activities(request,user)
    
    return context

def professor_dashboard_context(request, user):
    context = {
        'courses': [],
        'user': user
    }

    registrations = ProfessorCourseRegistration.objects.filter(professor=user)
    for prof_reg in registrations:  # for each professor registration
        course_dict = {'course': prof_reg.course,
                       'is_approved': prof_reg.is_approved}
        if prof_reg.is_approved:
            course_dict['students'] = {'registered': [], 'pending': []}
            # for each student registration
            for student_reg in StudentCourseRegistration.objects.filter(course=prof_reg.course):
                if student_reg.is_approved:
                    course_dict['students']['registered'].append(student_reg.student)
                else:
                    course_dict['students']['pending'].append(student_reg.student)
            course_dict['documents'] = prof_reg.course.documents.all()
            course_dict['homework'] = prof_reg.course.coursehomeworkrequest_set.all()
            course_dict['forum'] = prof_reg.course.forum
            course_dict['topics'] = prof_reg.course.course_topics.all()
        context['courses'].append(course_dict)

    return context


# loads NEW activities asynchronously, called with ajax
def new_dashboard_activities(request,user):
    last_id = long(request.GET.get('last_id'))

    own_course_activities = list(CourseActivity.objects.filter(
        Q(course__in=list(user.courses_enrolled.all()) + list(user.courses_managed.all())), ~Q(user=user), Q(id__gt=last_id) ).reverse())  

    # get all answers to posts that the user is following, except those in the users's own courses,
    # to avoid duplication
    # 
    forum_answer_activities = list(ForumAnswerActivity.objects.filter(
        Q(forum_answer__post__in=user.posts_following.all()), ~Q(user=user), Q(id__gt=last_id) ).exclude(
            forum_answer__post__forum__course__in = list(user.courses_enrolled.all()) + list(user.courses_managed.all())).reverse())
    
    activities_list = sorted(own_course_activities + forum_answer_activities, 
                key = lambda activity: activity.timestamp, 
                reverse=True)

    activities_context = [activity_context(activity,user) for activity in activities_list]


    return activities_context 
