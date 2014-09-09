from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# For wikis versioning
from django.contrib.contenttypes.models import ContentType
from versioning.models import Revision

from app.models import *
from app.ratings import *
from app.forum.context_processors import forum_stats_context, forum_answer_context, forum_post_context


def course_ratings_context(course, current_user=None):
    context = []
    allratings = course.rating_set.all()

    # All rating types
    for rating_type in RATING_TYPES:
        ratings = allratings.filter(rating_type=rating_type[0])

        rating = None
        if len(ratings) > 0:
            rating = sum([cur.rating for cur in ratings]) / len(ratings)
        # Add the general ratings
        context_rating = {
            'type': rating_type[1],
            'type_db': rating_type[0],
        }
        specific_rating = {
            'score': rating,
            'count': len(ratings)
        }
        if current_user:
            my_ratings = ratings.filter(user=current_user)
            if my_ratings:
                specific_rating['my_score'] = my_ratings[0].rating

        if rating_type[0] == PROFESSOR_R:
            professors = course.professors.all()
            for prof in professors:
                profratings = ratings.filter(professor=prof)
                profrating = None
                if profratings:
                    profrating = sum([cur.rating for cur in profratings]) / len(profratings)
                specific_rating = {
                    'score': profrating,
                    'count': len(profratings),
                    'professor': prof,
                }
                if current_user:
                    my_ratings = profratings.filter(user=current_user)
                    if my_ratings:
                        specific_rating['my_score'] = my_ratings[0].rating
                context.append(dict(context_rating.items() + specific_rating.items()))
        else:
            context.append(dict(context_rating.items() + specific_rating.items()))
    return context


def review_context(comment, current_user=None):
    context_comment = {
        'comment': comment
    }
    upvotes = comment.upvoted_by.all()
    downvotes = comment.downvoted_by.all()

    if not comment.anonymous:
        context_comment['posted_by'] = comment.posted_by

    nr_upvotes = upvotes.count()
    nr_downvotes = downvotes.count()
    context_comment['upvotes'] = nr_upvotes
    context_comment['downvotes'] = nr_downvotes
    if nr_downvotes >= 3:
        context_comment['dont_show'] = True
    if nr_downvotes >= 7:
        context_comment['dont_show_at_all'] = True

    if upvotes.filter(id=current_user.id).count() > 0:
        context_comment['upvoted'] = True
    if downvotes.filter(id=current_user.id).count() > 0:
        context_comment['downvoted'] = True

    return context_comment


def course_reviews_context(course, current_user=None):
    context = []
    reviews = course.review_set.all()
    for review in reviews:
        context.append(review_context(review, current_user))
    return context

def course_homework_count_submitted(course, homework_request):
    students = StudentCourseRegistration.objects.filter(course=course, is_approved=True)
    submissions = CourseHomeworkSubmission.objects.filter(homework_request=homework_request)
    cnt_submitted = 0
    for st in students:
        files_submitted = submissions.filter(submitter=st.student)
        if files_submitted.count() == homework_request.number_files:
            cnt_submitted += 1
    return cnt_submitted

def homework_context(hw, current_user):
    course = hw.course
    current_time = pytz.utc.localize(datetime.now())
    nr_students = StudentCourseRegistration.objects.filter(course=course, is_approved=True).count()

    within_deadline = hw.deadline.start <= current_time and current_time < hw.deadline.end
    is_allowed = course.get_registration_status(current_user) == COURSE_REGISTRATION_REGISTERED
    is_student = current_user.is_student_of(course)
    can_submit_homework = is_student and is_allowed and within_deadline
    
    homework_submissions = []
    if current_user.is_student():
        homework_submissions = CourseHomeworkSubmission.objects.filter(submitter=current_user, homework_request=hw)

    homework_submitted = course_homework_count_submitted(course, hw)

    context = {
        "homework": hw,
        "can_submit": can_submit_homework,
        "is_allowed": is_allowed,
        "previous_submissions": homework_submissions,
        "submitted": len(homework_submissions) == hw.number_files,
        "stats": {
            "submitted": homework_submitted,
            "students": nr_students
        }
    }
    if current_user.is_professor_of(course):
        context['active_hw'] = within_deadline
        context['coming_hw'] = hw.deadline.start > current_time
        context['past_hw'] = hw.deadline.end <= current_time

    return context

def course_homework_context(course, current_user):
    context = []
    all_homework = course.coursehomeworkrequest_set.all()
    for hw in all_homework:
        context.append(homework_context(hw, current_user))
    return context

def homework_dashboard_context(request, course, current_user):
    context = {}
    homework_requests = CourseHomeworkRequest.objects.filter(course=course)
    students = sorted(list(course.students.all()), key=lambda st:st.username)
    current_time = pytz.utc.localize(datetime.now())
    context['homework_requests'] = []

    for hw in homework_requests:
        all_submissions = CourseHomeworkSubmission.objects.filter(homework_request=hw)
        submissions_context = []
        for st in students:
            submissions = all_submissions.filter(submitter=st)
            submissions = sorted(submissions, key=lambda s:s.file_number)
            submissions_context.append({
                'student': st,
                'submissions': submissions,
                'file_numbers': [str(s.file_number) for s in submissions]
            })

        percentage_completed = 100.0 * all_submissions.count() / (hw.number_files * len(students))
        context['homework_requests'].append({
            'homework': hw,
            'all_submissions': submissions_context,
            'percentage_completed': percentage_completed,
            'ended': hw.deadline.end < current_time
        })

    # Course syllabus for topic editing
    context['syllabus'] = course_syllabus_context(course,current_user)

    # Is teacher
    context['teacher'] = {
        'is_teacher': True
    }

    return context

def course_syllabus_context(course, current_user):
    context = []
    for topic in course.course_topics.all():
        topic_context = {
            'topic': topic,
            'documents': topic.documents.all(),

        }
        if current_user in course.students.all() or current_user in course.professors.all():
            topic_context['homework'] = [hw for hw in course_homework_context(course,current_user) 
                                            if hw['homework'].course_topic == topic]

        context.append(topic_context)
    return context


# Professor extra settings
def course_teacher_dashboard(request, course, user):
    context = {
        'is_teacher': user.is_professor_of(course)
    }
    if not context['is_teacher']:
        return context

    registrations = ProfessorCourseRegistration.objects.filter(professor=user, course=course)
    if not registrations:
        return context
    prof_reg = registrations[0]

    context ['is_approved'] = prof_reg.is_approved

    if prof_reg.is_approved:
        context['students'] = {'registered': [], 'pending': []}
        # for each student registration
        student_registrations = StudentCourseRegistration.objects.filter(course=course)
        for student_reg in student_registrations:
            if student_reg.is_approved:
                context['students']['registered'].append(student_reg.student)
            else:
                context['students']['pending'].append(student_reg.student)

    context['forum_stats'] = forum_stats_context(course.forum)

    return context


def course_page_context(request, course):
    context = {}
    context['course'] = course
    context['hw_redirect_url'] = '/course/' + course.slug
    course_types = dict(COURSE_TYPES)
    # Course type seems to be not working?
    # context['course_type'] = course_types[course.course_type]
    context['professors'] = course.professors.all()

    # Current user
    current_user = None
    if request.user.is_authenticated():
        current_user = jUser.objects.get(id=request.user.id)

    # Ratings and comments
    context['ratings'] = course_ratings_context(course, current_user)
    context['comments'] = course_reviews_context(course, current_user)
    context['activities'] = course_activities(request, course)

    # Course path
    context['course_path'] = course.get_catalogue()
    context['semester'] = context['course_path'].split(" > ")[0]

    # User - Course Registration status (open|pending|registered|not allowed)
    registration_status = course.get_registration_status(current_user)
    registration_deadline = course.get_registration_deadline()  # course registration deadline

    # Is course registration open?
    registration_open = False
    if registration_deadline is not None:
        registration_open = registration_deadline.is_open()

    context['registration_status'] = registration_status
    context['registration_open'] = registration_open

    # Course syllabus
    context['syllabus'] = course_syllabus_context(course,current_user)

    # Course forum link
    context['forum'] = course.forum

    context['can_edit_wiki'] = course.can_edit_wiki(current_user)
    if hasattr(course, 'wiki'):
        context['wiki'] = course.wiki
        wiki_ctype = ContentType.objects.get(app_label="app", model="wikipage")
        content_object = wiki_ctype.get_object_for_this_type(pk=course.wiki.id)

        context['wiki_revisions'] = Revision.objects.filter(content_type=wiki_ctype, object_id=content_object.pk)

    context['documents'] = course.documents.all()
    context['can_upload_docs'] = current_user.is_professor_of(course)
    # Show documents/homework only if the user is registered and student/prof
    if current_user.is_student_of(course) or current_user.is_professor_of(course):
        context['all_homework'] = course_homework_context(course, current_user)
        context['current_homework'] = [hw for hw in context['all_homework'] if hw['is_allowed']]
        if current_user.is_professor_of(course):
            context['homework_has_active'] = [hw['active_hw'] for hw in context['all_homework']].count(True) > 0
            context['homework_has_coming'] = [hw['coming_hw'] for hw in context['all_homework']].count(True) > 0
            context['homework_has_past'] = [hw['past_hw'] for hw in context['all_homework']].count(True) > 0

    context['teacher'] = course_teacher_dashboard(request, course, current_user)

    return context


def course_activities(request, course):
    user = request.user.juser

    # Course activities 
    activities_list = list(CourseActivity.objects.filter(course=course).reverse())

    # Forum post activities
    activities_list += list(ForumPostActivity.objects.filter(forum_post__forum__forum_type=FORUM_COURSE,
                                                            forum_post__forum__forumcourse__course=course ))

    activities_list += list(ForumAnswerActivity.objects.filter(forum_answer__post__forum__forum_type=FORUM_COURSE,
                                                            forum_answer__post__forum__forumcourse__course=course ))

    activities_list = [a for a in activities_list if a.can_view(user)]
    activities_list = sorted(activities_list, key= lambda a: a.timestamp, reverse=True)
    
    activities_context = [activity_context(activity,user) for activity in activities_list]
    return paginated(request,activities_context, 20)



# loads NEW activities asynchronously, called with ajax
def new_course_activities(request,course):
    user = request.user.juser
    last_id = long(request.GET.get('last_id'))
    
    # Course activities 
    activities_list = list(CourseActivity.objects.filter(course=course,  id__gt=last_id).reverse())

    # Forum post activities
    activities_list += list(ForumPostActivity.objects.filter(forum_post__forum__forum_type=FORUM_COURSE,
                                                            forum_post__forum__forumcourse__course=course, id__gt=last_id ))

    activities_list += list(ForumAnswerActivity.objects.filter(forum_answer__post__forum__forum_type=FORUM_COURSE,
                                                            forum_answer__post__forum__forumcourse__course=course, id__gt=last_id))

    activities_list = [a for a in activities_list if a.can_view(user)]
    activities_list = sorted(activities_list, key= lambda a: a.timestamp, reverse=True)
    
    activities_context = [activity_context(activity,user) for activity in activities_list]

    return activities_context 


def activity_context(activity, current_user):
    activity_context = {
        "type": activity.get_type(),
        "activity": activity,
    }
    activity_type = activity_context["type"]
    activity_instance = activity.get_instance() # the most derived type


    if activity_type  == "ForumPostActivity":
        activity_context["post"] = forum_post_context(activity_instance.forum_post, current_user)
    elif activity_type == "ForumAnswerActivity":
        answer = activity_instance.forum_answer
        activity_context["answer"] = forum_answer_context(answer.post, answer, current_user)
    elif activity_type == "HomeworkActivity":
        activity_context['homework'] = homework_context(activity.homeworkactivity.homework, current_user)
    elif activity_type == "ReviewActivity":
        activity_context["review"] = review_context(activity_instance.review, current_user)
    elif activity_type == "WikiActivity":
        activity_context['contribution'] = activity_instance.contribution
    return activity_context
    
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