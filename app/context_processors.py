from django.template.loader import render_to_string
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


from app.models import *
from app.ratings import *
from app.forum.context_processors import forum_stats_context, forum_answer_context, forum_post_context
#from app.course.context_processors import *


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
    logged_in_user = request.user.juser # Should normally always be the same as user, adding this as a safety check
    last_id = request.GET.get('last_id', None)
    ACTIVITIES_PER_PAGE = 20

    # Get the (unevaluated) dashboard activities queryset
    activities_queryset = Activity.dashboard_page_activities(user)

    if last_id is not None:
        activities_queryset = activities_queryset.filter(id__lt=last_id)

    # Always get page 1, because we are filtering out activities with id >= last_id (so we're only getting the older ones from the db)
    filtered_list = paginate_activities(activities_queryset, 1, ACTIVITIES_PER_PAGE, logged_in_user)


    activities_context = [activity_context(activity,user) for activity in filtered_list]
    return activities_context


# loads NEW activities asynchronously, called with ajax
def new_dashboard_activities(request,user):
    logged_in_user = request.user.juser # Should normally always be the same as user, adding this as a safety check
    last_id = long(request.GET.get('last_id', 0))
    
    # Dashboard activities 
    activities_list = Activity.dashboard_page_activities(user).filter(id__gt=last_id)
    activities_list = [a for a in activities_list if a.can_view(logged_in_user)]

    activities_context = [activity_context(activity,user) for activity in activities_list]
    return activities_context

def dashboard_context(request):
    user = jUser.objects.get(id=request.user.id)

    context = {
        'courses': {'enrolled': [], 'assisted': [], 'managed': []},
        'schedule_items': [],
        'user': user,
        'hw_redirect_url': '/home'
    }

    registrations = StudentCourseRegistration.objects.filter(student = user)
    for reg in registrations:
        context['courses']['enrolled'].append({'course': reg.course, 'is_approved': reg.is_approved, 'homework': []})

    registrations = ProfessorCourseRegistration.objects.filter(professor=user)
    for reg in registrations:
        context['courses']['managed'].append({'course': reg.course, 'is_approved': reg.is_approved, 'homework': []})

    for c in user.courses_assisted.all():
        context['courses']['assisted'].append({'course': c, 'is_approved': True, 'homework': []})

    today =  datetime.combine(date.today(), datetime.min.time())
    tomorrow = today + timedelta(days=1)
    schedule_items = list(CourseAppointment.objects.filter( Q(Q(course__students=user) | Q(course__professors=user)),
                            Q(start__gte=pytz.utc.localize( today )),
                            Q(start__lte=pytz.utc.localize( tomorrow )))) +\
                        list(PersonalAppointment.objects.filter(user=user,
                            start__gte=pytz.utc.localize( today ),
                            start__lte=pytz.utc.localize( tomorrow )))

    context['schedule_items'] = sorted(schedule_items, key= lambda a: a.start) 

    for reg in context['courses']['enrolled']:
        if reg['is_approved']:
            course_hw = reg['course'].coursehomeworkrequest_set
            for homework in course_hw.filter(deadline__end__gte=pytz.utc.localize(datetime.now())):
                homework_submitted = CourseHomeworkSubmission.objects.filter(submitter=user,
                                                                             homework_request=homework).count() > 0
                if homework.can_view(user):
                    reg['homework'].append({'submitted': homework_submitted,
                                            'hw': homework})

    for reg in context['courses']['assisted']:
        if reg['is_approved']:
            course_hw = reg['course'].coursehomeworkrequest_set
            for homework in course_hw.filter(deadline__end__gte=pytz.utc.localize(datetime.now())):
                homework_submitted = CourseHomeworkSubmission.objects.filter(submitter=user,
                                                                             homework_request=homework).count() > 0
                reg['homework'].append({'submitted': homework_submitted,
                                        'hw': homework})

    for reg in context['courses']['managed']:
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


def activity_context(activity, current_user):
    import app.course.context_processors as course_cp
    import app.forum.context_processors as forum_cp
    activity_context = {
        "type": activity.get_type(),
        "activity": activity,
    }
    activity_type = activity_context["type"]
    activity_instance = activity.get_instance() # the most derived type


    if activity_type  == "ForumPostActivity":
        activity_context["post"] = forum_cp.forum_post_context(activity_instance.forum_post, current_user)
        if activity_instance.forum_post.forum.forum_type == FORUM_COURSE:
            activity_context["subtype"] = "forumcourse"
        else:
            activity_context["subtype"] ="forumgeneral"
    elif activity_type == "ForumAnswerActivity":
        answer = activity_instance.forum_answer
        activity_context["answer"] = forum_cp.forum_answer_context(answer.post, answer, current_user)
        if activity_instance.forum_answer.post.forum.forum_type == FORUM_COURSE:
            activity_context["subtype"] = "forumcourse"
        else:
            activity_context["subtype"] ="forumgeneral"
    elif activity_type == "HomeworkActivity":
        activity_context['homework'] = course_cp.homework_context(activity_instance.homework, current_user)
    elif activity_type == "ReviewActivity":
        activity_context["review"] = course_cp.review_context(activity_instance.review, current_user)
    elif activity_type == "WikiActivity":
        activity_context['contribution'] = activity_instance.contribution
    return activity_context

# If objects is an unevaluated queryset, it will only retrieve the objects of the requested page from the db
# Otherwise it slices the container into pages and returns the requested page
def paginated(objects, page_num, per_page):
    paginator = Paginator(objects, per_page)

    try:
        objects = paginator.page(page_num).object_list
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        objects = paginator.page(1).object_list
    except EmptyPage:
        objects = []

    return objects

def paginate_activities(activities_queryset, page, per_page, user):
    activities_list = paginated(activities_queryset, page, per_page)

    filtered_list = [a for a in activities_list if a.can_view(user)]
    if len(activities_list) == per_page:
        while len(filtered_list) < per_page:
            # Some entries were removed. Fill with new ones
            page += 1
            activities_list = paginated(activities_queryset, page, per_page)
            if len(activities_list) == 0: 
                # Nothing more to show
                break

            for a in activities_list:
                if a.can_view(user):
                    filtered_list.append(a)
                    if len(filtered_list)  >= per_page:
                        break

    return filtered_list