from django.template.loader import render_to_string
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


from app.models import *
from app.ratings import *
from app.course.context_processors import *


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


def dashboard_activities(request,user):
    user_courses = list(user.courses_enrolled.all()) + list(user.courses_managed.all())

    own_course_activities = list(CourseActivity.objects.filter(
        Q(course__in=list(user.courses_enrolled.all()) + list(user.courses_managed.all())), ~Q(user=user)).reverse())

    # get all answers to posts that the user is following, except those in the users's own courses,
    # to avoid duplication
    #
    forum_post_activities = list(ForumPostActivity.objects.filter(Q( 
                                Q (
                                    forum_post__forum__forum_type=FORUM_COURSE,
                                    forum_post__forum__forumcourse__course__in=user_courses
                                  )
                                |
                                Q (
                                    forum_post__followed_by = user
                                ), ~Q(user=user))).reverse())

    #activities_list += [ a for a in all_post_activities if user.is_student_of(a.get_course()) \
    #                                    or user.is_professor_of(a.get_course) \
    #                                        or user.is_admin_of(a.get_course) ]

    # Forum answer activities
    forum_answer_activities = list(ForumAnswerActivity.objects.filter(Q( 
                                Q (
                                    forum_answer__post__forum__forum_type = FORUM_COURSE ,
                                    forum_answer__post__forum__forumcourse__course__in = user_courses
                                  )
                                |
                                Q (
                                    forum_answer__post__followed_by = user
                                ), ~Q(user=user))).reverse())

    activities_list = sorted(own_course_activities + forum_post_activities + forum_answer_activities,
                             key=lambda activity: activity.timestamp, 
                             reverse=True)
    activities_list = [a for a in activities_list if a.can_view(user)]
    

    activities_context = [activity_context(activity,user) for activity in activities_list]
  
    return paginated(request,activities_context, 20)


# loads NEW activities asynchronously, called with ajax
def new_dashboard_activities(request,user):
    last_id = long(request.GET.get('last_id'))
    user_courses = list(user_courses_enrolled.all()) + list(user.courses_managed.all())
    own_course_activities = list(CourseActivity.objects.filter(
        Q(course__in=list(user.courses_enrolled.all()) + list(user.courses_managed.all())), ~Q(user=user), Q(id__gt=last_id) ).reverse())  

    # get all answers to posts that the user is following, except those in the users's own courses,
    # to avoid duplication
    # 
    forum_post_activities= ForumPostActivity.objects.filter(Q( 
                                Q (
                                     forum_post__forum__forum_type=FORUM_COURSE ,
                                     forum_post__forum__forumcourse__course__in=user_courses
                                  )
                                |
                                Q (
                                    forum_post__followed_by= user
                                )),~Q(user=user), Q(id__gt=last_id)).reverse()

    #activities_list += [ a for a in all_post_activities if user.is_student_of(a.get_course()) \
    #                                    or user.is_professor_of(a.get_course) \
    #                                        or user.is_admin_of(a.get_course) ]

    # Forum answer activities
    forum_answer_activities = ForumAnswerActivity.objects.filter(Q( 
                                Q (
                                    forum_answer__post__forum__forum_type=FORUM_COURSE,
                                    forum_answer__post__forum__forumcourse__course__in=user_courses
                                  )
                                |
                                Q (
                                    forum_answer__post__followed_by = user
                                )),~Q(user=user), Q(id__gt=last_id)).reverse()

    activities_list = sorted(own_course_activities +  forum_post_activities + forum_answer_activities, 
                key = lambda activity: activity.timestamp, 
                reverse=True)
    activities_list = [a for a in activities_list if a.can_view(user)]
    

    activities_context = [activity_context(activity,user) for activity in activities_list]


    return activities_context 


def dashboard_context(request):
    user = jUser.objects.get(id=request.user.id)

    context = {
        'courses': [],
        'schedule_items': [],
        'user': user,
        'hw_redirect_url': '/home'
    }

    registrations = StudentCourseRegistration.objects.filter(student = user)
    for reg in registrations:
        context['courses'].append({'course': reg.course, 'is_approved': reg.is_approved, 'homework': []})

    registrations = ProfessorCourseRegistration.objects.filter(professor=user)
    for reg in registrations:
        context['courses'].append({'course': reg.course, 'is_approved': reg.is_approved, 'homework': []})


    today =  datetime.combine(date.today(), datetime.min.time())
    tomorrow = today + timedelta(days=1)
    schedule_items = list(CourseAppointment.objects.filter( Q(Q(course__students=user) | Q(course__professors=user)),
                            Q(start__gte=pytz.utc.localize( today )),
                            Q(start__lte=pytz.utc.localize( tomorrow )))) +\
                        list(PersonalAppointment.objects.filter(user=user,
                            start__gte=pytz.utc.localize( today ),
                            start__lte=pytz.utc.localize( tomorrow )))

    context['schedule_items'] = sorted(schedule_items, key= lambda a: a.start) 

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



